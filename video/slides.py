"""Local HTML frames for the 90 second career showreel."""

from __future__ import annotations

import html

FONT_CSS = """
@font-face { font-family: Inter; src: url("file:///usr/share/fonts/truetype/macos/Inter-Regular.ttf"); font-weight: 400; }
@font-face { font-family: Inter; src: url("file:///usr/share/fonts/truetype/macos/Inter-Medium.ttf"); font-weight: 500; }
@font-face { font-family: Inter; src: url("file:///usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"); font-weight: 600; }
@font-face { font-family: Inter; src: url("file:///usr/share/fonts/truetype/macos/Inter-Bold.ttf"); font-weight: 700; }
@font-face { font-family: JB; src: url("file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"); font-weight: 400; }
@font-face { font-family: JB; src: url("file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"); font-weight: 500; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { overflow: hidden; }
body {
  font-family: Inter, sans-serif;
  color: #f4f1ea;
  background: #101418;
  -webkit-font-smoothing: antialiased;
}
.dark {
  width: 100%; height: 100%;
  background: radial-gradient(1100px 640px at 12% 0%, #1c2630 0%, transparent 55%), #101418;
  padding: 48px 64px 36px;
  display: flex; flex-direction: column;
}
header.top {
  display: flex; align-items: baseline; gap: 22px;
  font-family: JB, monospace; font-size: 20px; letter-spacing: 0.08em;
  text-transform: uppercase; color: #d4b483;
}
header.top .who { color: #f4f1ea; letter-spacing: 0.12em; }
header.top .spacer { flex: 1; }
.kicker {
  font-family: JB, monospace; color: #d4b483; letter-spacing: 0.14em;
  text-transform: uppercase; font-size: 18px; margin: 28px 0 12px;
}
h1 { font-weight: 600; font-size: 68px; line-height: 1.02; letter-spacing: -0.03em; }
.sub { color: #c9c2b6; font-size: 30px; line-height: 1.35; margin-top: 12px; }
.chips { display: flex; gap: 16px; margin-top: 36px; }
.chip {
  border: 1px solid #d4b483; color: #f4f1ea; border-radius: 999px;
  padding: 12px 22px; font-size: 26px;
}
.center { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.rule { width: 120px; height: 3px; background: #d4b483; margin: 18px 0; }
.timeline { margin-top: 28px; display: flex; gap: 28px; align-items: stretch; }
.node {
  width: 18px; border-radius: 9px; background: #d4b483; flex: none; margin-top: 8px;
}
.role { font-size: 28px; color: #d4b483; font-family: JB, monospace; letter-spacing: 0.04em; }
.focus { font-size: 40px; line-height: 1.25; max-width: 1400px; margin-top: 18px; }
.groups { display: flex; gap: 22px; margin-top: 22px; flex: 1; }
.group {
  flex: 1; background: #161c23; border: 1px solid #2c3540; border-radius: 18px; padding: 22px 22px 8px;
}
.group h2 { font-size: 22px; color: #d4b483; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; font-family: JB, monospace; }
.badge {
  display: block; margin-top: 12px; background: #101418; border: 1px solid #2c3540;
  border-radius: 12px; padding: 10px 14px; font-size: 26px;
}
.paper {
  width: 100%; height: 100%; background: #efeae2; color: #1e1a16;
  padding: 36px 48px 28px; display: flex; flex-direction: column; gap: 16px;
}
.paper header.top { color: #8a5a2a; }
.paper header.top .who { color: #1e1a16; }
.sample {
  font-family: JB, monospace; letter-spacing: 0.08em; text-transform: uppercase;
  background: #1e1a16; color: #f4f1ea; border-radius: 999px; padding: 8px 14px; font-size: 16px;
}
.flow { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 28px; }
.step {
  background: #f7f4ee; border: 1px solid #d9d0c3; border-radius: 14px; padding: 16px 18px;
  font-size: 24px; max-width: 320px;
}
.step b { display: block; font-size: 16px; letter-spacing: 0.08em; text-transform: uppercase; color: #8a5a2a; font-family: JB, monospace; font-weight: 500; }
.arrow { color: #8a5a2a; font-size: 28px; }
.health { display: flex; gap: 16px; }
.card {
  background: #f7f4ee; border: 1px solid #e0d8cc; border-radius: 16px; padding: 14px 16px; flex: 1;
}
.card b { display: block; font-size: 42px; letter-spacing: -0.03em; line-height: 1; }
.card span { display: block; margin-top: 6px; color: #5e574e; font-size: 16px; font-family: JB, monospace; letter-spacing: 0.06em; text-transform: uppercase; }
.below { color: #8d2b22; }
.bars { display: flex; gap: 10px; align-items: flex-end; height: 150px; }
.bar { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }
.bar i { display: block; width: 100%; }
.bar .p { background: #2f7d4a; }
.bar .f { background: #a33b32; }
.bar .s { background: #b7b1a6; }
.bar em { display: block; text-align: center; font-style: normal; font-size: 13px; color: #5e574e; margin-top: 4px; font-family: JB, monospace; }
.split { display: flex; gap: 18px; min-height: 0; flex: 1; }
.matrix { flex: 1.4; }
.flaky { flex: 0.8; }
table { width: 100%; border-collapse: collapse; font-size: 16px; }
th { text-align: left; font-family: JB, monospace; font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase; color: #6d675e; font-weight: 500; padding: 0 6px 6px; }
td { padding: 4px 6px; vertical-align: middle; }
td.name { font-family: JB, monospace; font-size: 15px; }
.dots { display: flex; gap: 3px; }
.dot { width: 14px; height: 14px; border-radius: 3px; display: inline-block; }
.dot.pass { background: #2f7d4a; }
.dot.fail { background: #a33b32; }
.dot.skip { background: #b7b1a6; }
.callout {
  background: #1e1a16; color: #f4f1ea; border-radius: 12px; padding: 12px 16px; font-size: 24px;
}
.rowitem { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid #e0d8cc; font-size: 20px; }
.kind { font-family: JB, monospace; font-size: 14px; letter-spacing: 0.06em; text-transform: uppercase; color: #8a5a2a; }
.chain { display: flex; gap: 14px; align-items: center; margin-top: 18px; }
.box {
  background: #161c23; border: 1px solid #2c3540; border-radius: 16px; padding: 18px 16px; min-width: 220px;
}
.box.on { border-color: #d4b483; }
.box small { display: block; color: #d4b483; font-family: JB, monospace; letter-spacing: 0.08em; text-transform: uppercase; font-size: 14px; }
.box strong { display: block; margin-top: 6px; font-size: 26px; font-weight: 600; }
.notes { display: flex; gap: 12px; margin-top: 22px; }
.note {
  flex: 1; border: 1px solid #2c3540; border-radius: 14px; padding: 14px 16px; color: #f4f1ea; font-size: 24px;
}
.steps { margin-top: 12px; display: flex; flex-direction: column; gap: 10px; }
.aitem { display: flex; gap: 16px; align-items: baseline; font-size: 30px; }
.num { font-family: JB, monospace; color: #d4b483; width: 48px; }
.ci {
  margin-top: auto; border-top: 1px solid #2c3540; padding-top: 16px; color: #c9c2b6; font-size: 26px;
}
.ship { margin-top: 20px; display: flex; flex-direction: column; gap: 14px; }
.ship div {
  background: #161c23; border-left: 4px solid #d4b483; border-radius: 12px; padding: 16px 20px; font-size: 36px;
}
.endgrid { flex: 1; display: flex; align-items: center; gap: 48px; }
.endcopy { flex: 1; }
.url { font-size: 36px; margin-top: 8px; }
.qr { width: 280px; height: 280px; background: #f4f1ea; border-radius: 16px; padding: 12px; }
.qr img { width: 100%; height: 100%; object-fit: contain; }
.og {
  width: 100%; height: 100%; padding: 56px 64px; display: flex; flex-direction: column; justify-content: center;
  background: radial-gradient(700px 420px at 100% 100%, #2a241c 0%, transparent 55%), #101418;
}
"""


def document(body: str, width: int, height: int) -> str:
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><style>"
        + FONT_CSS
        + f"body{{width:{width}px;height:{height}px;}}"
        + "</style></head><body>"
        + body
        + "</body></html>"
    )


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _clock(start: float, end: float) -> str:
    def fmt(seconds: float) -> str:
        total = int(round(seconds))
        return f"{total // 60}:{total % 60:02d}"

    return f"{fmt(start)}–{fmt(end)}"


def _top(index: str, start: float, end: float, light: bool = False) -> str:
    return (
        '<header class="top">'
        '<span class="who">Benjamin &quot;Beni&quot; Kun</span>'
        f"<span>{_esc(index)}</span>"
        '<span class="spacer"></span>'
        f"<span>{_clock(start, end)}</span>"
        "</header>"
    )


def intro_slide() -> str:
    body = f"""
    <div class="dark">
      {_top("01 / 09", 0, 6)}
      <div class="center">
        <p class="kicker">Career showreel</p>
        <h1>Benjamin &quot;Beni&quot; Kun</h1>
        <p class="sub">Senior QA Automation Engineer</p>
        <div class="chips">
          <span class="chip">Experience</span>
          <span class="chip">Tools</span>
          <span class="chip">Projects</span>
        </div>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def experience_slide() -> str:
    body = f"""
    <div class="dark">
      {_top("02 / 09", 6, 20)}
      <p class="kicker">Experience</p>
      <div class="timeline">
        <div class="node"></div>
        <div>
          <p class="role">current role · Present</p>
          <p class="focus">End-to-end automation, reporting, and CI for a multi-region SaaS platform.</p>
        </div>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def tools_slide() -> str:
    groups = [
        ("Automation", ["Python 3.13", "pytest", "pytest-xdist", "Playwright", "JUnit XML"]),
        ("Delivery", ["GitLab CI", "Kubernetes", "AWS S3", "CloudFront", "Slack API"]),
        ("Quality", ["Ruff", "mypy", "pydantic"]),
        ("Authoring", ["Chrome DevTools MCP", "ffmpeg", "edge-tts"]),
    ]
    columns = []
    for title, badges in groups:
        items = "".join(f'<span class="badge">{_esc(badge)}</span>' for badge in badges)
        columns.append(f'<section class="group"><h2>{_esc(title)}</h2>{items}</section>')
    body = f"""
    <div class="dark">
      {_top("03 / 09", 20, 32)}
      <p class="kicker">Tools and frameworks</p>
      <div class="groups">{''.join(columns)}</div>
    </div>
    """
    return document(body, 1920, 1080)


def pipeline_slide() -> str:
    steps = [
        ("01", "JUnit XML"),
        ("02", "Per-run HTML report"),
        ("03", "S3 behind CloudFront"),
        ("04", "Cumulative dashboard"),
        ("05", "Slack message with report link"),
    ]
    parts = []
    for index, (number, label) in enumerate(steps):
        if index:
            parts.append('<span class="arrow">→</span>')
        parts.append(f'<div class="step"><b>{number}</b>{_esc(label)}</div>')
    body = f"""
    <div class="paper">
      {_top("04 / 09", 32, 52)}
      <div style="display:flex;justify-content:space-between;align-items:flex-end">
        <div>
          <p class="kicker">Project 1</p>
          <h1 style="font-size:56px;color:#1e1a16">Automation dashboard</h1>
        </div>
        <span class="sample">Sample data</span>
      </div>
      <div class="flow">{''.join(parts)}</div>
    </div>
    """
    return document(body, 1920, 1080)


def dashboard_slide(sample: dict) -> str:
    peak = max(day["pass"] + day["fail"] + day["skip"] for day in sample["daily"]) or 1
    bars = []
    for day in sample["daily"]:
        total = day["pass"] + day["fail"] + day["skip"]
        height = 120 * total / peak
        def px(count: int) -> str:
            share = (count / total) * height if total else 0
            return f"{share:.1f}px"

        bars.append(
            '<div class="bar">'
            f'<i class="s" style="height:{px(day["skip"])}"></i>'
            f'<i class="f" style="height:{px(day["fail"])}"></i>'
            f'<i class="p" style="height:{px(day["pass"])}"></i>'
            f'<em>{_esc(day["day"].replace("Day ", "D"))}</em>'
            "</div>"
        )
    rows = []
    for test in sample["tests"]:
        cells = []
        for env in sample["envs"]:
            dots = "".join(
                f'<i class="dot {status}"></i>' for status in sample["matrix"][test][env]
            )
            cells.append(f'<td><span class="dots">{dots}</span></td>')
        rows.append(f'<tr><td class="name">{_esc(test)}</td>{"".join(cells)}</tr>')
    ranked = []
    for item in sample["ranked"]:
        ranked.append(
            '<div class="rowitem"><span>'
            f'{_esc(item["name"])}</span><span class="kind">{_esc(item["kind"])} · {_esc(item["fails"])} fails</span></div>'
        )
    rate = f"{sample['rate'] * 100:.1f}%"
    gate = f"{sample['gate'] * 100:.0f}%"
    health = "above sample gate" if sample["above_gate"] else "below sample gate"
    health_class = "" if sample["above_gate"] else "below"
    body = f"""
    <div class="paper">
      <header class="top">
        <span class="who">Automation dashboard</span>
        <span>04 / 09</span>
        <span class="spacer"></span>
        <span class="sample">Sample data</span>
      </header>
      <div class="health">
        <div class="card"><b class="{health_class}">{_esc(rate)}</b><span>sample pass rate</span></div>
        <div class="card"><b>{_esc(gate)}</b><span>sample quality gate</span></div>
        <div class="card"><b class="{health_class}">{_esc(health)}</b><span>sample health</span></div>
        <div class="card"><b>{sample["passed"]}/{sample["passed"] + sample["failed"] + sample["skipped"]}</b><span>pass / all sample cells</span></div>
      </div>
      <div class="bars">{''.join(bars)}</div>
      <div class="split">
        <div class="matrix">
          <table>
            <thead><tr><th>Test</th><th>dev</th><th>staging</th><th>prod</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </div>
        <div class="flaky">
          <p class="kind">Top of the sample list</p>
          {''.join(ranked)}
        </div>
      </div>
      <p class="callout">Flaky vs. broken, classified from run history.</p>
    </div>
    """
    return document(body, 1920, 1080)


def framework_slide() -> str:
    body = f"""
    <div class="dark">
      {_top("05 / 09", 52, 66)}
      <p class="kicker">Project 2 · Parallel-safe framework</p>
      <div class="chain">
        <div class="box on"><small>Test</small><strong>test</strong></div>
        <span>→</span>
        <div class="box on"><small>Page wrapper</small><strong>page object</strong></div>
        <span>→</span>
        <div class="box on"><small>Browser</small><strong>Playwright</strong></div>
      </div>
      <div class="chain">
        <div class="box"><small>pytest-xdist</small><strong>workers</strong></div>
        <span>→</span>
        <div class="box"><small>Shared</small><strong>one logged-in session</strong></div>
        <span>→</span>
        <div class="box"><small>Lock</small><strong>locked file</strong></div>
      </div>
      <div class="chain">
        <div class="box"><small>Pool</small><strong>scarce test-data pool</strong></div>
        <span>→</span>
        <div class="box"><small>Under a lock</small><strong>allocate and release</strong></div>
      </div>
      <div class="notes">
        <div class="note">nested logs</div>
        <div class="note">per-test artifacts</div>
        <div class="note">teardown cleanup</div>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def authoring_slide() -> str:
    steps = [
        "Inspect the live UI with Chrome DevTools MCP",
        "Choose semantic locators",
        "Scaffold page object and test",
        "Run a focused check",
        "Self-review against team standards",
    ]
    items = "".join(
        f'<div class="aitem"><span class="num">{index:02d}</span><span>{_esc(text)}</span></div>'
        for index, text in enumerate(steps, start=1)
    )
    body = f"""
    <div class="dark">
      {_top("07 / 09", 76, 86)}
      <p class="kicker">Project 4 · AI-assisted authoring and CI</p>
      <div class="steps">{items}</div>
      <p class="ci">Sanity jobs on dev checkout. Resource groups per shared pool. Artifacts kept.</p>
    </div>
    """
    return document(body, 1920, 1080)


def shipped_slide() -> str:
    items = [
        "eligibility and appeals flow automation",
        "driver API client",
        "flaky-test stabilization",
        "this video pipeline",
    ]
    body = f"""
    <div class="dark">
      {_top("08 / 09", 86, 88)}
      <p class="kicker">Also shipped</p>
      <div class="ship">{''.join(f'<div>{_esc(item)}</div>' for item in items)}</div>
    </div>
    """
    return document(body, 1920, 1080)


def end_slide() -> str:
    body = f"""
    <div class="dark">
      {_top("09 / 09", 88, 90)}
      <div class="endgrid">
        <div class="endcopy">
          <p class="kicker">Senior QA Automation Engineer</p>
          <h1>Benjamin &quot;Beni&quot; Kun</h1>
          <div class="rule"></div>
          <p class="url">https://benikun88.github.io/</p>
          <p class="url">https://www.linkedin.com/in/benjamin-kun</p>
        </div>
        <div class="qr"><img src="qr.png" alt="QR code for the site"></div>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def poster_slide() -> str:
    body = """
    <div class="dark">
      <div class="center">
        <p class="kicker">Senior QA Automation Engineer</p>
        <h1>Benjamin &quot;Beni&quot; Kun</h1>
        <p class="sub">Experience · Tools · Projects</p>
        <div class="rule"></div>
        <p class="url">benikun88.github.io</p>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def og_slide() -> str:
    body = """
    <div class="og">
      <p class="kicker">Senior QA Automation Engineer</p>
      <h1>Benjamin &quot;Beni&quot; Kun</h1>
      <p class="sub">Experience, tools, and projects</p>
      <div class="rule"></div>
      <p class="url">benikun88.github.io</p>
    </div>
    """
    return document(body, 1200, 630)
