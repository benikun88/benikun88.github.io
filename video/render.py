#!/usr/bin/env python3
"""Render the 60 second portfolio demo.

The shop footage is a headed Playwright run against
https://practicesoftwaretesting.com/ only. The report and dashboard
are screenshots of HTML built from that run's JUnit file.

    python video/render.py
    python video/render.py --preview-slides
    python video/render.py --reuse-build

Re-uses video/build artifacts when --reuse-build is set. Needs ffmpeg,
Playwright Chromium, and the packages in video/requirements.txt.
Headed Chromium is started under xvfb when DISPLAY is unset.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
VIDEO = Path(__file__).resolve().parent
BUILD = VIDEO / "build"
ASSETS = ROOT / "assets"
NARRATION_PATH = VIDEO / "narration.txt"
PUBLIC_SAMPLE = VIDEO / "public_sample"
PAGES_PY = PUBLIC_SAMPLE / "pages.py"
FPS = 30
LEAD = 0.32
TAIL = 0.28
MAX_TEMPO = 1.06
MEASURED_START = "# BEGIN MEASURED"
MEASURED_END = "# END MEASURED"
SHOP_URL = "https://practicesoftwaretesting.com/"

sys.path.insert(0, str(VIDEO))
from slides import (  # noqa: E402
    add_to_cart_lines,
    authoring_slide,
    ci_slide,
    dashboard_slide,
    end_card,
    og_card,
    poster_card,
    problem_slide,
    report_slide,
    snippet_lines_present,
    teaser_open,
)


@dataclass
class Chapter:
    start: float
    end: float
    key: str
    title: str
    text: str
    voice: str
    rate: str


@dataclass
class Cue:
    start: float
    end: float
    text: str


def ensure_display() -> None:
    if os.environ.get("DISPLAY") or "--preview-slides" in sys.argv:
        return
    if not shutil.which("xvfb-run"):
        raise SystemExit("DISPLAY is unset and xvfb-run is not installed.")
    os.execvp("xvfb-run", ["xvfb-run", "-a", sys.executable, *sys.argv])


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(raw)


def parse_narration(path: Path) -> tuple[list[Chapter], Chapter | None]:
    text = path.read_text(encoding="utf-8")
    if MEASURED_START in text:
        text = text.split(MEASURED_START)[0]
    voice = "en-US-AndrewNeural"
    rate = "-4%"
    chapters: list[Chapter] = []
    teaser: Chapter | None = None
    current: dict | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal current, teaser
        if current is None:
            return
        body = " ".join(part.strip() for part in buf if part.strip())
        chapter = Chapter(
            start=current["start"],
            end=current["end"],
            key=current["key"],
            title=current["title"],
            text=body,
            voice=voice,
            rate=rate,
        )
        if current["key"] == "teaser":
            teaser = chapter
        else:
            chapters.append(chapter)
        current = None
        buf.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("voice:"):
            voice = line.split(":", 1)[1].strip()
            continue
        if line.startswith("rate:"):
            rate = line.split(":", 1)[1].strip()
            continue
        chapter_match = re.match(
            r"\[chapter\s+([0-9.]+)\s+([0-9.]+)\s+(\w+)\s+\|\s+(.+)\]",
            line,
        )
        teaser_match = re.match(r"\[teaser\s+([0-9.]+)\]", line)
        if chapter_match or teaser_match:
            flush()
            if chapter_match:
                current = {
                    "start": float(chapter_match.group(1)),
                    "end": float(chapter_match.group(2)),
                    "key": chapter_match.group(3),
                    "title": chapter_match.group(4).strip(),
                }
            else:
                window = float(teaser_match.group(1))
                current = {
                    "start": 0.0,
                    "end": window,
                    "key": "teaser",
                    "title": "Teaser",
                }
            continue
        if current is not None:
            buf.append(line)
    flush()
    if not chapters:
        raise SystemExit(f"No chapters found in {path}")
    return chapters, teaser


def synthesize(text: str, voice: str, rate: str, mp3: Path) -> list[tuple[float, float, str]]:
    async def _run() -> list[tuple[float, float, str]]:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio = bytearray()
        cues: list[tuple[float, float, str]] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
            elif chunk["type"] == "SentenceBoundary":
                cues.append(
                    (
                        chunk["offset"] / 10_000_000,
                        chunk["duration"] / 10_000_000,
                        chunk["text"].strip(),
                    )
                )
        mp3.write_bytes(audio)
        return cues

    found = asyncio.run(_run())
    if not found:
        duration = probe_duration(mp3)
        return [(0.0, duration, text)]
    return found


def fit_speech(
    mp3: Path,
    wav: Path,
    window: float,
    cues: list[tuple[float, float, str]],
    origin: float,
) -> tuple[list[Cue], float]:
    spoken = probe_duration(mp3)
    available = window - LEAD - TAIL
    tempo = 1.0
    if spoken > available:
        tempo = spoken / available
        if tempo > MAX_TEMPO:
            raise SystemExit(
                f"Narration is {spoken:.2f}s in a {window:.2f}s window "
                f"(would need atempo {tempo:.3f}, limit {MAX_TEMPO}). Shorten the copy."
            )
    speech = wav.with_suffix(".speech.wav")
    filters = [f"atempo={tempo:.5f}"] if tempo > 1.01 else ["anull"]
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3),
            "-af",
            ",".join(filters),
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(speech),
        ]
    )
    spoken = probe_duration(speech)
    delay_ms = int(round(LEAD * 1000))
    # anullsrc is the clock. adelay alone does not extend a wav to the window.
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-t",
            f"{window:.3f}",
            "-i",
            "anullsrc=r=48000:cl=stereo",
            "-i",
            str(speech),
            "-filter_complex",
            (
                f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={delay_ms}:all=1,apad=pad_dur={window:.3f}[speech];"
                f"[0:a][speech]amix=inputs=2:duration=first:dropout_transition=0:"
                f"normalize=0,atrim=0:{window:.3f},asetpts=PTS-STARTPTS[a]"
            ),
            "-map",
            "[a]",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(wav),
        ]
    )
    actual = probe_duration(wav)
    if abs(actual - window) > 0.05:
        raise SystemExit(f"{wav.name} is {actual:.3f}s, wanted {window:.3f}s")
    scale = 1.0 / tempo
    fitted: list[Cue] = []
    for offset, duration, sentence in cues:
        start = origin + LEAD + (offset * scale)
        end = origin + LEAD + ((offset + duration) * scale)
        fitted.append(Cue(start=start, end=end, text=sentence))
    return fitted, tempo


def sentence_list(text: str) -> list[str]:
    parts = re.split(r"(?<=[.])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def run_pytest(junit_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PUBLIC_SAMPLE)
    print("+ pytest public sample", flush=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(PUBLIC_SAMPLE / "test_shop.py"),
            "--junitxml",
            str(junit_path),
            "-q",
        ],
        check=True,
        cwd=str(ROOT),
        env=env,
    )


def parse_junit(path: Path) -> dict:
    tree = ET.parse(path)
    root = tree.getroot()
    suites = list(root.iter("testsuite"))
    cases = list(root.iter("testcase"))
    tests = []
    for case in cases:
        status = "passed"
        if case.find("failure") is not None:
            status = "failed"
        elif case.find("error") is not None:
            status = "error"
        elif case.find("skipped") is not None:
            status = "skipped"
        tests.append(
            {
                "name": case.attrib.get("name", "test"),
                "status": status,
                "time": float(case.attrib.get("time", "0") or 0),
            }
        )
    totals = {
        "tests_total": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "time": 0.0,
    }
    for suite in suites:
        totals["tests_total"] += int(suite.attrib.get("tests", "0") or 0)
        totals["failed"] += int(suite.attrib.get("failures", "0") or 0)
        totals["errors"] += int(suite.attrib.get("errors", "0") or 0)
        totals["skipped"] += int(suite.attrib.get("skipped", "0") or 0)
        totals["time"] += float(suite.attrib.get("time", "0") or 0)
    if not totals["tests_total"]:
        totals["tests_total"] = len(tests)
        totals["time"] = sum(item["time"] for item in tests)
        totals["failed"] = sum(item["status"] == "failed" for item in tests)
        totals["errors"] = sum(item["status"] == "error" for item in tests)
    passed = sum(item["status"] == "passed" for item in tests)
    py = platform.python_version()
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "python": py,
        "python_short": ".".join(py.split(".")[:2]),
        "pytest": version("pytest"),
        "playwright": version("playwright"),
        "target": SHOP_URL,
        "tests": tests,
        "passed": passed,
        **totals,
    }


def cache_product_images(browser) -> dict[str, bytes]:
    """Product photos answer 403 as subresources from this network.

    A top-level GET of the same public URL returns the image. Cache those
    bytes so the live page can render them.
    """
    import json
    import urllib.request

    request = urllib.request.Request(
        "https://api.practicesoftwaretesting.com/products?page=1",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    names = []
    for item in payload.get("data", []):
        image = item.get("product_image") or {}
        if image.get("file_name"):
            names.append(image["file_name"])
    cache: dict[str, bytes] = {}
    context = browser.new_context()
    page = context.new_page()
    try:
        for name in names:
            url = f"https://practicesoftwaretesting.com/assets/img/products/{name}"
            fetched = page.goto(url, wait_until="load", timeout=20_000)
            content_type = (fetched.headers.get("content-type") or "") if fetched else ""
            if fetched and fetched.ok and content_type.startswith("image/"):
                cache[url] = fetched.body()
    finally:
        context.close()
    print(f"cached {len(cache)} product photos", flush=True)
    return cache


def record_tour(out_dir: Path) -> Path:
    from pages import Shop

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.webm"):
        old.unlink()
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute("data-test")
        browser = playwright.chromium.launch(
            headless=False,
            args=["--disable-dev-shm-usage"],
        )
        photos = cache_product_images(browser)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(out_dir),
            record_video_size={"width": 1920, "height": 1080},
            locale="en-US",
        )

        def fulfill_photo(route) -> None:
            url = route.request.url.split("?", 1)[0]
            body = photos.get(url)
            if body:
                route.fulfill(status=200, content_type="image/avif", body=body)
            else:
                route.continue_()

        if photos:
            context.route("**/assets/img/products/**", fulfill_photo)
        context.add_init_script(
            """
            const style = document.createElement("style");
            style.textContent = "[data-test='chat-toggle'], [data-test='live-activity-toggle'] { display: none !important; }";
            document.documentElement.appendChild(style);
            """
        )
        page = context.new_page()
        page.set_default_timeout(25_000)
        shop = Shop(page)
        shop.open_home()
        page.get_by_test_id("product-name").first.scroll_into_view_if_needed()
        page.wait_for_timeout(1400)
        page.screenshot(path=str(out_dir / "home.png"))
        shop.open_first_in_stock_product()
        page.get_by_test_id("add-to-cart").scroll_into_view_if_needed()
        page.wait_for_timeout(1700)
        shop.add_to_cart()
        page.wait_for_timeout(1400)
        shop.open_cart()
        page.get_by_test_id("cart-total").wait_for(state="visible")
        page.wait_for_timeout(2400)
        page.screenshot(path=str(out_dir / "cart.png"))
        context.close()
        browser.close()
    videos = sorted(out_dir.glob("*.webm"))
    if not videos:
        raise SystemExit("Playwright did not write a tour video.")
    return videos[-1]


def shoot(page, html: str, path: Path, size: tuple[int, int]) -> None:
    html_path = BUILD / "stills" / f"{path.stem}.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.goto(html_path.as_uri())
    page.wait_for_timeout(40)
    if path.suffix == ".jpg":
        page.screenshot(path=str(path), type="jpeg", quality=90)
    elif path.suffix == ".png":
        page.screenshot(path=str(path), type="png")
    else:
        raise SystemExit(f"Unsupported screenshot type: {path}")


def live_overlay(path: Path) -> None:
    image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    medium = ImageFont.truetype(
        "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf",
        22,
    )

    def pill(text: str, x: int, y: int, anchor: str) -> None:
        box = draw.textbbox((0, 0), text, font=medium)
        width = box[2] - box[0]
        height = box[3] - box[1]
        pad_x, pad_y = 16, 10
        if anchor == "right":
            left = x - width - pad_x * 2
        elif anchor == "center":
            left = x - (width // 2) - pad_x
        else:
            left = x
        top = y
        rect = (left, top, left + width + pad_x * 2, top + height + pad_y * 2)
        draw.rounded_rectangle(rect, radius=16, fill=(16, 20, 24, 214))
        draw.text((left + pad_x, top + pad_y - 2), text, font=medium, fill=(244, 241, 234, 255))

    pill("02  /  05    LIVE RUN", 36, 28, "left")
    pill("HEADED PLAYWRIGHT   ·   PUBLIC PRACTICE SHOP   ·   SYNTHETIC DATA", 960, 980, "center")
    image.save(path)


def still_clip(image: Path, frames: int, dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(image),
            "-frames:v",
            str(frames),
            "-r",
            str(FPS),
            "-vf",
            "scale=1920:1080,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "16",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dest),
        ]
    )


def live_clip(tour: Path, overlay: Path, frames: int, dest: Path) -> None:
    duration = probe_duration(tour)
    target = frames / FPS
    if duration > target + 0.05:
        speed = target / duration
        video = (
            f"[0:v]setpts=PTS*{speed:.6f},fps={FPS},scale=1920:1080,"
            f"trim=duration={target:.3f},setpts=PTS-STARTPTS[base]"
        )
    else:
        pad = max(0.0, target - duration)
        video = (
            f"[0:v]fps={FPS},scale=1920:1080,setsar=1,"
            f"tpad=stop_mode=clone:stop_duration={pad:.3f}[base]"
        )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(tour),
            "-i",
            str(overlay),
            "-filter_complex",
            video + ";[base][1:v]overlay=0:0:format=auto,fps=30,format=yuv420p[out]",
            "-map",
            "[out]",
            "-frames:v",
            str(frames),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "16",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dest),
        ]
    )


def html_for(chapter: Chapter, index: int, run_info: dict, lines: list[str]) -> str:
    sentences = [cue.text for cue in _CHAPTER_CUES[chapter.key]]
    if chapter.key == "problem":
        return problem_slide(sentences, index, run_info["python_short"])
    if chapter.key == "reports":
        if index <= 1:
            return report_slide(run_info)
        if index == 2:
            return dashboard_slide(run_info, "counts")
        if index == 3:
            return dashboard_slide(run_info, "publish")
        return dashboard_slide(run_info, "slack")
    if chapter.key == "ci":
        return ci_slide(index)
    if chapter.key == "authoring":
        if index >= 2:
            return end_card(run_info["python_short"])
        return authoring_slide(highlight_wait=(index == 1), lines=lines)
    raise SystemExit(f"No slide for {chapter.key}")


_CHAPTER_CUES: dict[str, list[Cue]] = {}


def write_measured(chapters: list[Chapter], cues: list[Cue], tempos: dict[str, float], teaser_cues: list[Cue]) -> None:
    original = NARRATION_PATH.read_text(encoding="utf-8")
    if MEASURED_START in original:
        original = original.split(MEASURED_START)[0].rstrip() + "\n"
    else:
        original = original.rstrip() + "\n"

    def stamp(seconds: float) -> str:
        millis = int(round(seconds * 1000))
        hours, rem = divmod(millis, 3_600_000)
        minutes, rem = divmod(rem, 60_000)
        secs, ms = divmod(rem, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"

    lines = [
        MEASURED_START,
        "# Cue times include the 0.32s lead at each chapter. Rewritten by video/render.py.",
    ]
    for key, tempo in tempos.items():
        if tempo > 1.01:
            lines.append(f"# {key} speech sped by atempo {tempo:.3f}")
    lines.append("")
    for cue in cues:
        lines.append(f"{stamp(cue.start)} --> {stamp(cue.end)}")
        lines.append(cue.text)
        lines.append("")
    if teaser_cues:
        lines.append("# teaser")
        for cue in teaser_cues:
            lines.append(f"{stamp(cue.start)} --> {stamp(cue.end)}")
            lines.append(cue.text)
            lines.append("")
    lines.append(MEASURED_END)
    lines.append("")
    NARRATION_PATH.write_text(original + "\n" + "\n".join(lines), encoding="utf-8")


def wrap_caption(text: str, width: int = 42) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if current and len(trial) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return "\n".join(lines)


def write_vtt(cues: list[Cue], path: Path, note: str) -> None:
    def stamp(seconds: float) -> str:
        millis = int(round(max(0.0, seconds) * 1000))
        hours, rem = divmod(millis, 3_600_000)
        minutes, rem = divmod(rem, 60_000)
        secs, ms = divmod(rem, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"

    blocks = ["WEBVTT", "", f"NOTE", note, ""]
    for index, cue in enumerate(cues, start=1):
        blocks.append(str(index))
        blocks.append(f"{stamp(cue.start)} --> {stamp(cue.end)}")
        blocks.append(wrap_caption(cue.text))
        blocks.append("")
    path.write_text("\n".join(blocks), encoding="utf-8")


def concat_and_encode(clips: list[Path], audio: Path, dest: Path, burn_vtt: Path | None = None) -> None:
    args = ["ffmpeg", "-y"]
    for clip in clips:
        args.extend(["-i", str(clip)])
    args.extend(["-i", str(audio)])
    count = len(clips)
    chain = "".join(f"[{index}:v]" for index in range(count))
    video = f"{chain}concat=n={count}:v=1:a=0,format=yuv420p"
    video += ",drawbox=x=0:y=1074:w='iw*t/60':h=6:color=0xD4B483"
    if burn_vtt is not None:
        # Teaser uses its own duration. Caller passes a filter override by dest name.
        pass
    args.extend(
        [
            "-filter_complex",
            f"{video}[v]",
            "-map",
            "[v]",
            "-map",
            f"{count}:a",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "26",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            "-t",
            "60",
            str(dest),
        ]
    )
    run(args)


def encode_teaser(clips: list[Path], audio: Path, vtt: Path, dest: Path) -> None:
    args = ["ffmpeg", "-y"]
    for clip in clips:
        args.extend(["-i", str(clip)])
    args.extend(["-i", str(audio)])
    count = len(clips)
    chain = "".join(f"[{index}:v]" for index in range(count))
    style = (
        "FontName=Inter\\,FontSize=18\\,PrimaryColour=&H00EAF4F1\\,"
        "BackColour=&H00141810\\,BorderStyle=3\\,Outline=6\\,Shadow=0\\,"
        "Alignment=2\\,MarginV=72"
    )
    sub = str(vtt).replace("\\", "\\\\").replace(":", "\\:")
    video = (
        f"{chain}concat=n={count}:v=1:a=0,format=yuv420p,"
        f"subtitles='{sub}':force_style='{style}'[v]"
    )
    args.extend(
        [
            "-filter_complex",
            video,
            "-map",
            "[v]",
            "-map",
            f"{count}:a",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "26",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            "-t",
            "20",
            str(dest),
        ]
    )
    run(args)


def concat_audio(parts: list[Path], dest: Path) -> None:
    args = ["ffmpeg", "-y"]
    for part in parts:
        args.extend(["-i", str(part)])
    chain = "".join(f"[{index}:a]" for index in range(len(parts)))
    args.extend(
        [
            "-filter_complex",
            f"{chain}concat=n={len(parts)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
            "-map",
            "[a]",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(dest),
        ]
    )
    run(args)


def moov_before_mdat(path: Path) -> bool:
    blob = path.read_bytes()
    return blob.find(b"moov") != -1 and blob.find(b"moov") < blob.find(b"mdat")


def preview_slides() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    sample = {
        "generated": "2026-11-07 00:00 UTC",
        "python": platform.python_version(),
        "python_short": ".".join(platform.python_version().split(".")[:2]),
        "pytest": version("pytest"),
        "playwright": version("playwright"),
        "target": SHOP_URL,
        "tests": [
            {"name": "test_home_lists_products", "status": "passed", "time": 1.2},
            {"name": "test_product_shows_price", "status": "passed", "time": 1.4},
            {"name": "test_cart_total_after_add", "status": "passed", "time": 1.8},
        ],
        "tests_total": 3,
        "passed": 3,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "time": 4.4,
    }
    source = PAGES_PY.read_text(encoding="utf-8")
    lines = add_to_cart_lines(source)
    frames = {
        "problem": problem_slide(sentence_list(parse_narration(NARRATION_PATH)[0][0].text), 0, sample["python_short"]),
        "report": report_slide(sample),
        "dashboard": dashboard_slide(sample, "publish"),
        "ci": ci_slide(3),
        "authoring": authoring_slide(True, lines),
        "end": end_card(sample["python_short"]),
        "poster": poster_card(sample["python_short"]),
        "og": og_card(sample["python_short"]),
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        for name, html in frames.items():
            size = (1200, 630) if name == "og" else (1920, 1080)
            shoot(page, html, BUILD / f"preview-{name}.png", size)
        browser.close()
    print("preview written to", BUILD)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the portfolio demo video.")
    parser.add_argument("--preview-slides", action="store_true")
    parser.add_argument("--reuse-build", action="store_true")
    args = parser.parse_args()
    if args.preview_slides:
        preview_slides()
        return

    snippet_lines_present(PAGES_PY.read_text(encoding="utf-8"))
    if platform.python_version_tuple()[:2] != ("3", "13"):
        raise SystemExit(f"Sample interpreter must be Python 3.13, found {platform.python_version()}")

    BUILD.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    audio_dir = BUILD / "audio"
    stills = BUILD / "stills"
    clips = BUILD / "clips"
    for folder in (audio_dir, stills, clips):
        folder.mkdir(parents=True, exist_ok=True)

    chapters, teaser = parse_narration(NARRATION_PATH)
    source = PAGES_PY.read_text(encoding="utf-8")
    lines = add_to_cart_lines(source)

    all_cues: list[Cue] = []
    tempos: dict[str, float] = {}
    wavs: list[Path] = []
    for chapter in chapters:
        mp3 = audio_dir / f"{chapter.key}.mp3"
        wav = audio_dir / f"{chapter.key}.wav"
        if args.reuse_build and mp3.exists() and wav.exists():
            raw_cues = synthesize(chapter.text, chapter.voice, chapter.rate, mp3)
        else:
            raw_cues = synthesize(chapter.text, chapter.voice, chapter.rate, mp3)
        fitted, tempo = fit_speech(mp3, wav, chapter.end - chapter.start, raw_cues, chapter.start)
        tempos[chapter.key] = tempo
        all_cues.extend(fitted)
        _CHAPTER_CUES[chapter.key] = fitted
        wavs.append(wav)
        print(f"{chapter.key}: tempo {tempo:.3f}, cues {len(fitted)}", flush=True)

    teaser_cues: list[Cue] = []
    teaser_wav = audio_dir / "teaser.wav"
    if teaser is not None:
        teaser_mp3 = audio_dir / "teaser.mp3"
        raw = synthesize(teaser.text, teaser.voice, teaser.rate, teaser_mp3)
        teaser_cues, teaser_tempo = fit_speech(
            teaser_mp3, teaser_wav, teaser.end - teaser.start, raw, 0.0
        )
        tempos["teaser"] = teaser_tempo

    narration_wav = audio_dir / "narration.wav"
    concat_audio(wavs, narration_wav)
    narration_length = probe_duration(narration_wav)
    if narration_length < 59.95:
        padded = audio_dir / "narration-padded.wav"
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(narration_wav),
                "-af",
                f"apad=pad_dur={60 - narration_length + 0.05:.3f},atrim=0:60",
                "-c:a",
                "pcm_s16le",
                "-ar",
                "48000",
                "-ac",
                "2",
                str(padded),
            ]
        )
        padded.replace(narration_wav)
    elif narration_length > 60.05:
        raise SystemExit(f"Narration is {narration_length:.3f}s, expected 60s")
    write_measured(chapters, all_cues, tempos, teaser_cues)
    write_vtt(
        all_cues,
        ASSETS / "captions.vtt",
        "English narration for the portfolio demo. Timed to the rendered voice.",
    )
    if teaser_cues:
        write_vtt(
            teaser_cues,
            ASSETS / "teaser.vtt",
            "English narration for the 20 second cut. Timed to the rendered voice.",
        )

    junit = BUILD / "junit.xml"
    if not (args.reuse_build and junit.exists()):
        run_pytest(junit)
    run_info = parse_junit(junit)
    (BUILD / "run.json").write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    if run_info["failed"] or run_info["errors"]:
        raise SystemExit(f"Public sample had failures: {run_info}")

    tour_dir = BUILD / "tour"
    tour = None
    existing = sorted(tour_dir.glob("*.webm")) if tour_dir.exists() else []
    if args.reuse_build and existing:
        tour = existing[-1]
    else:
        sys.path.insert(0, str(PUBLIC_SAMPLE))
        tour = record_tour(tour_dir)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        plans: list[tuple[Path, int]] = []
        for chapter in chapters:
            total = int(round((chapter.end - chapter.start) * FPS))
            if chapter.key == "live":
                overlay = stills / "live-overlay.png"
                live_overlay(overlay)
                dest = clips / "live.mp4"
                live_clip(tour, overlay, total, dest)
                plans.append((dest, total))
                continue
            cues = _CHAPTER_CUES[chapter.key]
            spans: list[tuple[int, float]] = []
            for index, cue in enumerate(cues):
                begin = chapter.start if index == 0 else cue.start
                finish = cues[index + 1].start if index + 1 < len(cues) else chapter.end
                spans.append((index, max(0.05, finish - begin)))
            raw = [span for _, span in spans]
            weights = [max(1, int(round(part / sum(raw) * total))) for part in raw]
            weights[-1] += total - sum(weights)
            if chapter.key == "authoring" and len(weights) >= 2:
                # Keep the site URL on screen for at least five seconds.
                minimum = 5 * FPS
                if weights[-1] < minimum:
                    take = min(minimum - weights[-1], max(0, weights[-2] - FPS))
                    weights[-2] -= take
                    weights[-1] += take
            for (index, _), frames in zip(spans, weights):
                image = stills / f"{chapter.key}-{index:02d}.png"
                shoot(page, html_for(chapter, index, run_info, lines), image, (1920, 1080))
                dest = clips / f"{chapter.key}-{index:02d}.mp4"
                still_clip(image, frames, dest)
                plans.append((dest, frames))
        shoot(page, poster_card(run_info["python_short"]), ASSETS / "poster.jpg", (1920, 1080))
        shoot(page, og_card(run_info["python_short"]), ASSETS / "og-card.png", (1200, 630))
        shoot(page, teaser_open(), stills / "teaser-open.png", (1920, 1080))
        shoot(page, end_card(run_info["python_short"]), stills / "teaser-end.png", (1920, 1080))
        # Dashboard still already written as reports-02 or later. Grab publish focus explicitly.
        shoot(page, dashboard_slide(run_info, "counts"), stills / "teaser-dash.png", (1920, 1080))
        browser.close()

    picture_clips = [path for path, _frames in plans]
    concat_and_encode(picture_clips, narration_wav, ASSETS / "demo.mp4")

    # 20s teaser: open 4s, live 9s, dashboard 4s, end 3s. 120+270+120+90 = 600 frames.
    if teaser_wav.exists():
        still_clip(stills / "teaser-open.png", 120, clips / "teaser-open.mp4")
        live_clip(tour, stills / "live-overlay.png", 270, clips / "teaser-live.mp4")
        still_clip(stills / "teaser-dash.png", 120, clips / "teaser-dash.mp4")
        still_clip(stills / "teaser-end.png", 90, clips / "teaser-end.mp4")
        encode_teaser(
            [
                clips / "teaser-open.mp4",
                clips / "teaser-live.mp4",
                clips / "teaser-dash.mp4",
                clips / "teaser-end.mp4",
            ],
            teaser_wav,
            ASSETS / "teaser.vtt",
            ASSETS / "teaser.mp4",
        )

    webm = ASSETS / "demo.webm"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(ASSETS / "demo.mp4"),
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "34",
            "-b:v",
            "0",
            "-deadline",
            "good",
            "-cpu-used",
            "4",
            "-row-mt",
            "1",
            "-c:a",
            "libopus",
            "-b:a",
            "96k",
            str(webm),
        ]
    )

    demo = ASSETS / "demo.mp4"
    info = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(demo),
        ],
        text=True,
    )
    (BUILD / "ffprobe-demo.json").write_text(info, encoding="utf-8")
    size = demo.stat().st_size
    if size > 25 * 1024 * 1024:
        raise SystemExit(
            f"{demo} is {size / 1024 / 1024:.1f} MB, over 25 MB. "
            "Do not commit it. Fall back to an unlisted youtube-nocookie.com embed."
        )
    if not moov_before_mdat(demo):
        raise SystemExit("demo.mp4 moov atom is not before mdat (faststart missing).")
    print("demo.mp4", size, "faststart ok")
    print("demo.webm", webm.stat().st_size)
    print("poster", (ASSETS / "poster.jpg").stat().st_size)
    print("og", (ASSETS / "og-card.png").stat().st_size)
    if (ASSETS / "teaser.mp4").exists():
        print("teaser", (ASSETS / "teaser.mp4").stat().st_size)


if __name__ == "__main__":
    ensure_display()
    main()
