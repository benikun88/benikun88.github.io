#!/usr/bin/env python3
"""Render the 90 second career showreel.

Shop footage is a headed Playwright recording of
https://practicesoftwaretesting.com/ only. The dashboard is synthetic
sample data from video/sample_data.py.

    python video/render.py
    python video/render.py --preview-slides
    python video/render.py --reuse-build

The 1920x1080 master is written outside the repo. Web files land in assets/.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
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
import segno
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
VIDEO = Path(__file__).resolve().parent
BUILD = VIDEO / "build"
ASSETS = ROOT / "assets"
NARRATION_PATH = VIDEO / "narration.txt"
STORYBOARD_PATH = VIDEO / "storyboard.html"
PUBLIC_SAMPLE = VIDEO / "public_sample"
MASTER = Path("/home/ubuntu/showreel-master.mp4")
FPS = 30
LEAD = 0.20
TAIL = 0.15
MAX_TEMPO = 1.08
MEASURED_START = "# BEGIN MEASURED"
MEASURED_END = "# END MEASURED"
SHOP_URL = "https://practicesoftwaretesting.com/"
WIDTH = 1920
HEIGHT = 1080

sys.path.insert(0, str(VIDEO))
from sample_data import build_sample  # noqa: E402
from slides import (  # noqa: E402
    authoring_slide,
    dashboard_slide,
    end_slide,
    experience_slide,
    framework_slide,
    intro_slide,
    og_slide,
    pipeline_slide,
    poster_slide,
    shipped_slide,
    tools_slide,
)

# Terms are stored encoded so the plaintext is not part of the source.
_ENCODED_TERMS = (
    "Vmlh",
    "UmlkZSB3aXRoIFZpYQ==",
    "cmlkZXdpdGh2aWE=",
    "cmlkZXdpdGh2aWEuY29t",
    "TW9vdml0",
    "U01BUlRTSE9PVEVS",
    "U21hcnQgU2hvb3Rlcg==",
    "U21hcnRzaG9vdGVy",
    "UXVhbGl0ZXN0",
    "U2NvZGl4",
    "QXRlcmE=",
    "Um9iaW4=",
    "QHJpZGV3aXRodmlhLmNvbQ==",
)
_WORD_TERMS = {base64.b64decode(item).decode() for item in ("Vmlh", "Um9iaW4=")}


@dataclass
class Chapter:
    start: float
    end: float
    key: str
    title: str
    text: str
    voice: str
    rate: str
    teaser: bool = False


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


def parse_narration(path: Path) -> tuple[list[Chapter], list[Chapter]]:
    text = path.read_text(encoding="utf-8")
    if MEASURED_START in text:
        text = text.split(MEASURED_START)[0]
    voice = "en-US-AndrewNeural"
    rate = "-4%"
    main: list[Chapter] = []
    teaser: list[Chapter] = []
    current: dict | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal current
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
            teaser=current["teaser"],
        )
        (teaser if chapter.teaser else main).append(chapter)
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
        matched = re.match(
            r"\[(chapter|teaser)\s+([0-9.]+)\s+([0-9.]+)\s+(\w+)\s+\|\s+(.+)\]",
            line,
        )
        if matched:
            flush()
            current = {
                "teaser": matched.group(1) == "teaser",
                "start": float(matched.group(2)),
                "end": float(matched.group(3)),
                "key": matched.group(4),
                "title": matched.group(5).strip(),
            }
            continue
        if current is not None:
            buf.append(line)
    flush()
    if not main:
        raise SystemExit(f"No chapters found in {path}")
    return main, teaser


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
        return [(0.0, probe_duration(mp3), text)]
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
            "ffmpeg", "-y", "-i", str(mp3), "-af", ",".join(filters),
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(speech),
        ]
    )
    delay_ms = int(round(LEAD * 1000))
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-t", f"{window:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-i", str(speech),
            "-filter_complex",
            (
                f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={delay_ms}:all=1,apad=pad_dur={window:.3f}[speech];"
                f"[0:a][speech]amix=inputs=2:duration=first:dropout_transition=0:"
                f"normalize=0,atrim=0:{window:.3f},asetpts=PTS-STARTPTS[a]"
            ),
            "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(wav),
        ]
    )
    actual = probe_duration(wav)
    if abs(actual - window) > 0.08:
        raise SystemExit(f"{wav.name} is {actual:.3f}s, wanted {window:.3f}s")
    scale = 1.0 / tempo
    fitted = [
        Cue(
            start=origin + LEAD + (offset * scale),
            end=origin + LEAD + ((offset + duration) * scale),
            text=sentence,
        )
        for offset, duration, sentence in cues
    ]
    return fitted, tempo


def wrap_caption(text: str, width: int = 42) -> list[str]:
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
    return lines


def _caption_pieces(text: str) -> list[str]:
    pieces: list[str] = []
    bucket: list[str] = []
    for word in text.split():
        trial = " ".join(bucket + [word])
        if bucket and len(wrap_caption(trial)) > 2:
            pieces.append(" ".join(bucket))
            bucket = [word]
        else:
            bucket.append(word)
    if bucket:
        pieces.append(" ".join(bucket))
    return pieces


def layout_captions(cues: list[Cue]) -> list[Cue]:
    """At most two lines, at most 17 characters per second, no overlaps.

    A fast sentence may hold on screen into the pause before the next sentence.
    """
    laid: list[Cue] = []
    for index, cue in enumerate(cues):
        nxt = cues[index + 1].start if index + 1 < len(cues) else cue.end + 8
        available = max(0.2, nxt - cue.start - 0.005)
        pieces = _caption_pieces(cue.text)
        if len(cue.text) / available > 17:
            raise SystemExit(f"Caption rate too high at {cue.start:.3f}s")
        needed = len(cue.text) / 17
        span = min(available, max(cue.end - cue.start, needed))
        total_chars = sum(len(piece) for piece in pieces) or 1
        cursor = cue.start
        for piece_index, piece in enumerate(pieces):
            if piece_index == len(pieces) - 1:
                end = cue.start + span
            else:
                end = cursor + span * (len(piece) / total_chars)
            end = min(end, nxt - 0.005)
            if end <= cursor:
                raise SystemExit(f"Caption overlap at {cursor:.3f}s")
            if len(piece) / (end - cursor) > 17.05:
                raise SystemExit(f"Caption rate too high at {cursor:.3f}s")
            if len(wrap_caption(piece)) > 2:
                raise SystemExit(f"Caption exceeds two lines at {cursor:.3f}s")
            laid.append(Cue(start=cursor, end=end, text=piece))
            cursor = end
    return laid


def stamp(seconds: float, srt: bool = False) -> str:
    millis = int(round(max(0.0, seconds) * 1000))
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    sep = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{sep}{ms:03d}"


def write_captions(cues: list[Cue], vtt: Path, srt: Path | None, note: str) -> None:
    blocks = ["WEBVTT", "", "NOTE", note, ""]
    srt_blocks: list[str] = []
    for index, cue in enumerate(cues, start=1):
        text = "\n".join(wrap_caption(cue.text))
        blocks.extend([str(index), f"{stamp(cue.start)} --> {stamp(cue.end)}", text, ""])
        srt_blocks.extend([str(index), f"{stamp(cue.start, srt=True)} --> {stamp(cue.end, srt=True)}", text, ""])
    vtt.write_text("\n".join(blocks), encoding="utf-8")
    if srt is not None:
        srt.write_text("\n".join(srt_blocks), encoding="utf-8")


def write_measured(chapters: list[Chapter], cues: list[Cue], tempos: dict[str, float], teaser_cues: list[Cue]) -> None:
    original = NARRATION_PATH.read_text(encoding="utf-8")
    if MEASURED_START in original:
        original = original.split(MEASURED_START)[0].rstrip() + "\n"
    else:
        original = original.rstrip() + "\n"
    lines = [MEASURED_START, "# Cue times include the lead-in. Rewritten by video/render.py."]
    for key, tempo in tempos.items():
        if tempo > 1.01:
            lines.append(f"# {key} speech sped by atempo {tempo:.3f}")
    lines.append("")
    for cue in cues:
        lines.extend([f"{stamp(cue.start)} --> {stamp(cue.end)}", cue.text, ""])
    if teaser_cues:
        lines.append("# teaser")
        for cue in teaser_cues:
            lines.extend([f"{stamp(cue.start)} --> {stamp(cue.end)}", cue.text, ""])
    lines.extend([MEASURED_END, ""])
    NARRATION_PATH.write_text(original + "\n" + "\n".join(lines), encoding="utf-8")


def concat_audio(parts: list[Path], dest: Path) -> None:
    args = ["ffmpeg", "-y"]
    for part in parts:
        args.extend(["-i", str(part)])
    chain = "".join(f"[{index}:a]" for index in range(len(parts)))
    args.extend(
        [
            "-filter_complex",
            f"{chain}concat=n={len(parts)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
            "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(dest),
        ]
    )
    run(args)


def run_pytest(junit_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PUBLIC_SAMPLE)
    print("+ pytest public sample", flush=True)
    subprocess.run(
        [
            sys.executable, "-m", "pytest", str(PUBLIC_SAMPLE / "test_shop.py"),
            "--junitxml", str(junit_path), "-q",
        ],
        check=True,
        cwd=str(ROOT),
        env=env,
    )


def parse_junit(path: Path) -> dict:
    root = ET.parse(path).getroot()
    tests = []
    for case in root.iter("testcase"):
        if case.find("failure") is not None:
            status = "failed"
        elif case.find("error") is not None:
            status = "error"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        tests.append({"name": case.attrib.get("name", "test"), "status": status, "time": float(case.attrib.get("time", "0") or 0)})
    failed = sum(item["status"] == "failed" for item in tests)
    errors = sum(item["status"] == "error" for item in tests)
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "python": platform.python_version(),
        "pytest": version("pytest"),
        "playwright": version("playwright"),
        "target": SHOP_URL,
        "tests": tests,
        "passed": sum(item["status"] == "passed" for item in tests),
        "failed": failed,
        "errors": errors,
        "tests_total": len(tests),
    }


def cache_product_images(browser) -> dict[str, bytes]:
    import urllib.request

    request = urllib.request.Request(
        "https://api.practicesoftwaretesting.com/products?page=1",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    names = [
        item["product_image"]["file_name"]
        for item in payload.get("data", [])
        if (item.get("product_image") or {}).get("file_name")
    ]
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
        browser = playwright.chromium.launch(headless=False, args=["--disable-dev-shm-usage"])
        photos = cache_product_images(browser)
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            record_video_dir=str(out_dir),
            record_video_size={"width": WIDTH, "height": HEIGHT},
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
        page = context.new_page()
        page.set_default_timeout(25_000)
        shop = Shop(page)
        shop.open_home()
        shop.search("hammer")
        page.get_by_test_id("product-name").first.scroll_into_view_if_needed()
        page.wait_for_timeout(1100)
        page.screenshot(path=str(out_dir / "search.png"))
        shop.filter_category("Hand Tools")
        page.wait_for_timeout(900)
        shop.open_first_in_stock_product()
        page.get_by_test_id("add-to-cart").scroll_into_view_if_needed()
        page.wait_for_timeout(800)
        shop.add_to_cart()
        page.wait_for_timeout(1300)
        page.screenshot(path=str(out_dir / "added.png"))
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
    page.wait_for_timeout(60)
    if path.suffix == ".jpg":
        page.screenshot(path=str(path), type="jpeg", quality=90)
    else:
        page.screenshot(path=str(path), type="png")


def live_overlay(path: Path, passed: int, total: int) -> None:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    medium = ImageFont.truetype("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf", 22)
    large = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf", 28)

    def pill(text: str, x: int, y: int, anchor: str, font) -> None:
        box = draw.textbbox((0, 0), text, font=font)
        width = box[2] - box[0]
        height = box[3] - box[1]
        pad_x, pad_y = 16, 10
        left = x - (width // 2) - pad_x if anchor == "center" else x
        rect = (left, y, left + width + pad_x * 2, y + height + pad_y * 2)
        draw.rounded_rectangle(rect, radius=16, fill=(16, 20, 24, 220))
        draw.text((left + pad_x, y + pad_y - 2), text, font=font, fill=(244, 241, 234, 255))

    pill("06  /  09    LIVE RUN", 36, 28, "left", medium)
    pill("HEADED PLAYWRIGHT   ·   PUBLIC PRACTICE SHOP", 960, 980, "center", medium)
    if total and passed == total:
        pill(f"PUBLIC SAMPLE   ·   {passed} PASSED", 36, 900, "left", large)
    image.save(path)


def still_clip(image: Path, frames: int, dest: Path) -> None:
    run(
        [
            "ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(image),
            "-frames:v", str(frames), "-r", str(FPS),
            "-vf", f"scale={WIDTH}:{HEIGHT},format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-an", str(dest),
        ]
    )


def live_clip(tour: Path, overlay: Path, frames: int, dest: Path) -> None:
    # The recording starts on a blank document. Skip that lead-in.
    lead = 1.7
    duration = max(0.5, probe_duration(tour) - lead)
    target = frames / FPS
    if duration > target + 0.05:
        speed = target / duration
        video = (
            f"[0:v]trim=start={lead:.3f},setpts=PTS-STARTPTS,setpts=PTS*{speed:.6f},"
            f"fps={FPS},scale={WIDTH}:{HEIGHT},trim=duration={target:.3f},setpts=PTS-STARTPTS[base]"
        )
    else:
        pad = max(0.0, target - duration)
        video = (
            f"[0:v]trim=start={lead:.3f},setpts=PTS-STARTPTS,fps={FPS},"
            f"scale={WIDTH}:{HEIGHT},setsar=1,tpad=stop_mode=clone:stop_duration={pad:.3f}[base]"
        )
    run(
        [
            "ffmpeg", "-y", "-i", str(tour), "-i", str(overlay),
            "-filter_complex", video + ";[base][1:v]overlay=0:0:format=auto,fps=30,format=yuv420p[out]",
            "-map", "[out]", "-frames:v", str(frames), "-r", str(FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-an", str(dest),
        ]
    )


def concat_video(clips: list[Path], audio: Path, dest: Path, seconds: float, burn: Path | None = None) -> None:
    args = ["ffmpeg", "-y"]
    for clip in clips:
        args.extend(["-i", str(clip)])
    args.extend(["-i", str(audio)])
    count = len(clips)
    chain = "".join(f"[{index}:v]" for index in range(count))
    video = f"{chain}concat=n={count}:v=1:a=0,format=yuv420p,drawbox=x=0:y=1074:w='iw*t/{seconds:.0f}':h=6:color=0xD4B483"
    if burn is not None:
        style = (
            "FontName=Inter\\,FontSize=18\\,PrimaryColour=&H00EAF4F1\\,"
            "BackColour=&H00141810\\,BorderStyle=3\\,Outline=6\\,Shadow=0\\,"
            "Alignment=2\\,MarginV=80"
        )
        sub = str(burn).replace("\\", "\\\\").replace(":", "\\:")
        video += f",subtitles='{sub}':force_style='{style}'"
    args.extend(
        [
            "-filter_complex", f"{video}[v]",
            "-map", "[v]", "-map", f"{count}:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", "-t", f"{seconds:.3f}",
            "-metadata", "title=Benjamin Kun career showreel",
            str(dest),
        ]
    )
    run(args)


def export_web(master: Path) -> None:
    web = ASSETS / "demo.mp4"
    run(
        [
            "ffmpeg", "-y", "-i", str(master),
            "-vf", "scale=1280:720,format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-crf", "28",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart",
            "-metadata", "title=Benjamin Kun career showreel",
            str(web),
        ]
    )
    run(
        [
            "ffmpeg", "-y", "-i", str(web),
            "-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p", "-crf", "36", "-b:v", "0",
            "-deadline", "good", "-cpu-used", "4", "-row-mt", "1",
            "-c:a", "libopus", "-b:a", "96k",
            str(ASSETS / "demo.webm"),
        ]
    )


def export_teaser(clips: list[Path], audio: Path, vtt: Path) -> None:
    args = ["ffmpeg", "-y"]
    for clip in clips:
        args.extend(["-i", str(clip)])
    args.extend(["-i", str(audio)])
    count = len(clips)
    chain = "".join(f"[{index}:v]" for index in range(count))
    style = (
        "FontName=Inter\\,FontSize=16\\,PrimaryColour=&H00EAF4F1\\,"
        "BackColour=&H00141810\\,BorderStyle=3\\,Outline=6\\,Shadow=0\\,"
        "Alignment=2\\,MarginV=64"
    )
    sub = str(vtt).replace("\\", "\\\\").replace(":", "\\:")
    video = (
        f"{chain}concat=n={count}:v=1:a=0,scale=1280:720,format=yuv420p,"
        f"subtitles='{sub}':force_style='{style}'[v]"
    )
    args.extend(
        [
            "-filter_complex", video,
            "-map", "[v]", "-map", f"{count}:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "28",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", "-t", "30",
            str(ASSETS / "teaser.mp4"),
        ]
    )
    run(args)


def moov_before_mdat(path: Path) -> bool:
    blob = path.read_bytes()
    return blob.find(b"moov") != -1 and blob.find(b"moov") < blob.find(b"mdat")


def count_terms(text: str) -> int:
    hits = 0
    for encoded in _ENCODED_TERMS:
        term = base64.b64decode(encoded).decode()
        if term in _WORD_TERMS:
            hits += len(re.findall(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE))
        else:
            hits += text.lower().count(term.lower())
    return hits


def sanitize(extra_dirs: list[Path]) -> None:
    groups = {
        "storyboard": [STORYBOARD_PATH],
        "narration": [NARRATION_PATH],
        "captions": [ASSETS / "captions.vtt", ASSETS / "captions.srt", ASSETS / "teaser.vtt"],
        "metadata": [VIDEO / "slides.py", VIDEO / "sample_data.py", VIDEO / "render.py"],
    }
    for label, paths in groups.items():
        hits = 0
        braces = 0
        for path in paths:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            hits += count_terms(text)
            if label in {"storyboard", "captions"}:
                braces += text.count("{{")
        print(f"sanitize.{label} {hits}")
        if hits:
            raise SystemExit(f"sanitize.{label} failed")
        if braces:
            raise SystemExit(f"placeholder braces in {label}")
    name_hits = 0
    for folder in [VIDEO, ASSETS, *extra_dirs]:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if "build" in path.parts and path.suffix in {".png", ".jpg", ".html", ".wav", ".mp3", ".mp4", ".webm"}:
                if path.suffix == ".html":
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    name_hits += count_terms(text)
                    if "{{" in text:
                        raise SystemExit("placeholder braces in a frame")
                continue
            name_hits += count_terms(path.name)
    print(f"sanitize.filenames {name_hits}")
    if name_hits:
        raise SystemExit("sanitize.filenames failed")


def render_speech(chapters: list[Chapter], audio_dir: Path) -> tuple[list[Cue], list[Path], dict[str, float]]:
    cues: list[Cue] = []
    wavs: list[Path] = []
    tempos: dict[str, float] = {}
    for chapter in chapters:
        mp3 = audio_dir / f"{'t-' if chapter.teaser else ''}{chapter.key}.mp3"
        wav = audio_dir / f"{'t-' if chapter.teaser else ''}{chapter.key}.wav"
        raw = synthesize(chapter.text, chapter.voice, chapter.rate, mp3)
        fitted, tempo = fit_speech(mp3, wav, chapter.end - chapter.start, raw, chapter.start)
        tempos[("teaser-" if chapter.teaser else "") + chapter.key] = tempo
        cues.extend(fitted)
        wavs.append(wav)
        print(f"{chapter.key}: tempo {tempo:.3f}, cues {len(fitted)}", flush=True)
    return cues, wavs, tempos


def preview_slides() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    sample = build_sample()
    stills = BUILD / "stills"
    stills.mkdir(parents=True, exist_ok=True)
    segno.make("https://benikun88.github.io/", error="m").save(stills / "qr.png", scale=8, border=2, dark="#101418", light="#f4f1ea")
    frames = {
        "intro": intro_slide(),
        "experience": experience_slide(),
        "tools": tools_slide(),
        "pipeline": pipeline_slide(),
        "dashboard": dashboard_slide(sample),
        "framework": framework_slide(),
        "authoring": authoring_slide(),
        "shipped": shipped_slide(),
        "end": end_slide(),
        "poster": poster_slide(),
        "og": og_slide(),
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        for name, html in frames.items():
            size = (1200, 630) if name == "og" else (WIDTH, HEIGHT)
            shoot(page, html, BUILD / f"preview-{name}.png", size)
        browser.close()
    print("preview written", BUILD)


def spot_check(master: Path) -> None:
    out = BUILD / "spot"
    out.mkdir(parents=True, exist_ok=True)
    for second in (0, 6, 20, 32, 38, 52, 66, 76, 86, 88):
        run(["ffmpeg", "-y", "-ss", str(second), "-i", str(master), "-frames:v", "1", str(out / f"t{second:02d}.jpg")])
    print("spot frames", out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the career showreel.")
    parser.add_argument("--preview-slides", action="store_true")
    parser.add_argument("--reuse-build", action="store_true")
    args = parser.parse_args()
    if args.preview_slides:
        preview_slides()
        return

    if "{{" in STORYBOARD_PATH.read_text(encoding="utf-8"):
        raise SystemExit("placeholder braces in storyboard")
    BUILD.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    audio_dir = BUILD / "audio"
    stills = BUILD / "stills"
    clips = BUILD / "clips"
    for folder in (audio_dir, stills, clips):
        folder.mkdir(parents=True, exist_ok=True)

    chapters, teaser_chapters = parse_narration(NARRATION_PATH)
    main_cues, main_wavs, tempos = render_speech(chapters, audio_dir)
    teaser_cues, teaser_wavs, teaser_tempos = render_speech(teaser_chapters, audio_dir)
    tempos.update(teaser_tempos)
    narration_wav = audio_dir / "narration.wav"
    concat_audio(main_wavs, narration_wav)
    teaser_wav = audio_dir / "teaser.wav"
    concat_audio(teaser_wavs, teaser_wav)
    main_caps = layout_captions(main_cues)
    teaser_caps = layout_captions(teaser_cues)
    write_measured(chapters, main_caps, tempos, teaser_caps)
    write_captions(main_caps, ASSETS / "captions.vtt", ASSETS / "captions.srt", "English narration for the career showreel.")
    write_captions(teaser_caps, ASSETS / "teaser.vtt", None, "English narration for the 30 second cut.")

    junit = BUILD / "junit.xml"
    if not (args.reuse_build and junit.exists()):
        run_pytest(junit)
    run_info = parse_junit(junit)
    (BUILD / "run.json").write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    if run_info["failed"] or run_info["errors"] or run_info["passed"] != run_info["tests_total"]:
        raise SystemExit(f"Public sample did not pass: {run_info}")

    tour_dir = BUILD / "tour"
    existing = sorted(tour_dir.glob("*.webm")) if tour_dir.exists() else []
    if args.reuse_build and existing:
        tour = existing[-1]
    else:
        sys.path.insert(0, str(PUBLIC_SAMPLE))
        tour = record_tour(tour_dir)

    sample = build_sample()
    segno.make("https://benikun88.github.io/", error="m").save(
        stills / "qr.png", scale=8, border=2, dark="#101418", light="#f4f1ea"
    )
    visuals = {
        "intro": intro_slide(),
        "experience": experience_slide(),
        "tools": tools_slide(),
        "pipeline": pipeline_slide(),
        "dashboard": dashboard_slide(sample),
        "framework": framework_slide(),
        "authoring": authoring_slide(),
        "shipped": shipped_slide(),
        "end": end_slide(),
    }
    spans = [
        (0, 6, "intro"), (6, 20, "experience"), (20, 32, "tools"),
        (32, 38, "pipeline"), (38, 52, "dashboard"), (52, 66, "framework"),
        (66, 76, "live"), (76, 86, "authoring"), (86, 88, "shipped"), (88, 90, "end"),
    ]
    picture: list[Path] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        for start, end, key in spans:
            frames = int(round((end - start) * FPS))
            if key == "live":
                overlay = stills / "live-overlay.png"
                live_overlay(overlay, run_info["passed"], run_info["tests_total"])
                dest = clips / "live.mp4"
                live_clip(tour, overlay, frames, dest)
            else:
                image = stills / f"{key}.png"
                shoot(page, visuals[key], image, (WIDTH, HEIGHT))
                dest = clips / f"{key}.mp4"
                still_clip(image, frames, dest)
            picture.append(dest)
        shoot(page, poster_slide(), ASSETS / "poster.jpg", (WIDTH, HEIGHT))
        shoot(page, og_slide(), ASSETS / "og-card.png", (1200, 630))
        browser.close()

    concat_video(picture, narration_wav, MASTER, 90)
    export_web(MASTER)
    teaser_picture = [clips / "intro.mp4", clips / "experience.mp4", clips / "dashboard.mp4"]
    # Dashboard highlight is 10s; the full dashboard clip is 14s. Trim by re-encoding 300 frames.
    dash_short = clips / "dashboard-10.mp4"
    run(
        [
            "ffmpeg", "-y", "-i", str(clips / "dashboard.mp4"),
            "-frames:v", "300", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "16", "-pix_fmt", "yuv420p", "-an", str(dash_short),
        ]
    )
    export_teaser([teaser_picture[0], teaser_picture[1], dash_short], teaser_wav, ASSETS / "teaser.vtt")

    web = ASSETS / "demo.mp4"
    if web.stat().st_size > 25 * 1024 * 1024:
        raise SystemExit("Web MP4 exceeds 25 MB")
    if not moov_before_mdat(web):
        raise SystemExit("Web MP4 is missing faststart")
    main_dur = probe_duration(MASTER)
    teaser_dur = probe_duration(ASSETS / "teaser.mp4")
    if not 88 <= main_dur <= 92:
        raise SystemExit(f"Master duration {main_dur:.2f}s is outside 88-92")
    if not 28 <= teaser_dur <= 32:
        raise SystemExit(f"Teaser duration {teaser_dur:.2f}s is outside 28-32")
    sanitize([stills])
    spot_check(MASTER)
    print("master", MASTER, MASTER.stat().st_size, f"{main_dur:.3f}s")
    print("web", web, web.stat().st_size)
    print("webm", (ASSETS / "demo.webm").stat().st_size)
    print("teaser", (ASSETS / "teaser.mp4").stat().st_size, f"{teaser_dur:.3f}s")


if __name__ == "__main__":
    ensure_display()
    main()
