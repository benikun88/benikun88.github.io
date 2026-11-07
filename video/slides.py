"""Local HTML frames for the demo. No external images or network fonts."""

from __future__ import annotations

import html
from typing import Any

FONT_CSS = """
@font-face {
  font-family: Inter;
  src: url("file:///usr/share/fonts/truetype/macos/Inter-Regular.ttf");
  font-weight: 400;
}
@font-face {
  font-family: Inter;
  src: url("file:///usr/share/fonts/truetype/macos/Inter-Medium.ttf");
  font-weight: 500;
}
@font-face {
  font-family: Inter;
  src: url("file:///usr/share/fonts/truetype/macos/Inter-SemiBold.ttf");
  font-weight: 600;
}
@font-face {
  font-family: Inter;
  src: url("file:///usr/share/fonts/truetype/macos/Inter-Bold.ttf");
  font-weight: 700;
}
@font-face {
  font-family: JB;
  src: url("file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf");
  font-weight: 400;
}
@font-face {
  font-family: JB;
  src: url("file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf");
  font-weight: 500;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { overflow: hidden; }
body {
  font-family: Inter, sans-serif;
  color: #f4f1ea;
  background: #101418;
  -webkit-font-smoothing: antialiased;
}
.dark {
  width: 100%;
  height: 100%;
  background:
    radial-gradient(1200px 700px at 15% 0%, #1c2630 0%, transparent 55%),
    #101418;
  padding: 56px 72px 40px;
  display: flex;
  flex-direction: column;
}
header.top {
  display: flex;
  align-items: baseline;
  gap: 28px;
  font-family: JB, monospace;
  font-size: 22px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #d4b483;
}
header.top .who { color: #f4f1ea; letter-spacing: 0.12em; }
header.top .spacer { flex: 1; }
.split { flex: 1; display: flex; align-items: center; gap: 72px; }
.thesis { width: 640px; flex: none; }
.kicker {
  font-family: JB, monospace;
  color: #d4b483;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 20px;
  margin-bottom: 22px;
}
h1 {
  font-weight: 500;
  font-size: 68px;
  line-height: 1.05;
  letter-spacing: -0.03em;
  max-width: 640px;
}
.tools {
  margin-top: 36px;
  color: #a8b0b8;
  font-size: 26px;
  line-height: 1.45;
}
ol.beats { list-style: none; flex: 1; }
ol.beats li {
  font-size: 34px;
  line-height: 1.35;
  color: #5e6872;
  padding: 14px 0 14px 22px;
  border-left: 3px solid #2a3340;
}
ol.beats li.past { color: #c9c2b6; }
ol.beats li.now {
  color: #f4f1ea;
  border-left-color: #d4b483;
}
.paper {
  width: 100%;
  height: 100%;
  background: #efeae2;
  color: #1e1a16;
  padding: 48px 64px 36px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.paper header.top { color: #8a5a2a; }
.paper header.top .who { color: #1e1a16; }
.report-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
}
.report-title h1 { font-size: 64px; color: #1e1a16; }
.sub {
  margin-top: 8px;
  color: #5e574e;
  font-size: 24px;
}
.pill {
  font-family: JB, monospace;
  font-size: 22px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 12px 18px;
  border-radius: 999px;
}
.pill.pass { background: #e5f4ec; color: #14643c; }
.pill.fail { background: #fde8e4; color: #8d2b22; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.stat {
  background: #f7f4ee;
  border: 1px solid #e0d8cc;
  border-radius: 16px;
  padding: 18px 22px;
}
.stat b { display: block; font-size: 40px; font-weight: 600; letter-spacing: -0.03em; }
.stat span {
  display: block;
  margin-top: 4px;
  color: #6d675e;
  font-family: JB, monospace;
  font-size: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
table { width: 100%; border-collapse: collapse; font-size: 26px; }
th {
  text-align: left;
  font-family: JB, monospace;
  font-size: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6d675e;
  font-weight: 500;
  padding: 0 12px 12px;
  border-bottom: 1px solid #d9d0c3;
}
td { padding: 16px 12px; border-bottom: 1px solid #e4dcd0; vertical-align: middle; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
td.name { font-family: JB, monospace; font-size: 24px; }
.ok { color: #14643c; }
.bad { color: #8d2b22; }
.note { color: #5e574e; font-size: 22px; line-height: 1.4; max-width: 1500px; }
.steps { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.step {
  font-family: JB, monospace;
  font-size: 20px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid #d9d0c3;
  color: #5e574e;
  background: #f7f4ee;
}
.step.on { border-color: #8a5a2a; color: #1e1a16; background: #f3e6d4; }
.arrow { color: #b3aa9e; font-size: 22px; }
.dash-nums { display: flex; gap: 28px; align-items: stretch; }
.big {
  flex: 1;
  background: #f7f4ee;
  border-radius: 20px;
  border: 1px solid #e0d8cc;
  padding: 28px 32px;
}
.big b { display: block; font-size: 92px; letter-spacing: -0.04em; line-height: 0.95; font-weight: 600; }
.big span { display: block; margin-top: 12px; font-size: 24px; color: #5e574e; }
.nodes { display: flex; gap: 16px; align-items: stretch; margin-top: 36px; }
.node {
  flex: 1;
  background: #171d24;
  border: 1px solid #2c3540;
  border-radius: 18px;
  min-height: 150px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.node small {
  font-family: JB, monospace;
  font-size: 16px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #8b97a3;
}
.node strong { font-size: 30px; font-weight: 500; letter-spacing: -0.02em; }
.node.on { border-color: #d4b483; background: #241c14; }
.node.on small { color: #d4b483; }
.chips { display: flex; gap: 16px; margin-top: 18px; }
.chip {
  flex: 1;
  border: 1px solid #2c3540;
  border-radius: 14px;
  padding: 16px 18px;
  color: #8b97a3;
  font-size: 24px;
}
.chip.on { color: #f4f1ea; border-color: #d4b483; }
.disclaimer { margin-top: auto; color: #8b97a3; font-size: 22px; }
.columns { flex: 1; display: flex; gap: 28px; align-items: stretch; margin-top: 28px; }
.panel {
  flex: 1;
  background: #161c23;
  border: 1px solid #2c3540;
  border-radius: 20px;
  padding: 28px 30px;
  display: flex;
  flex-direction: column;
}
.panel h2 { font-size: 32px; font-weight: 500; letter-spacing: -0.02em; }
.panel .hint { color: #8b97a3; margin: 8px 0 18px; font-size: 20px; }
dl.kv { display: flex; flex-direction: column; gap: 10px; }
dl.kv div {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
}
dl.kv dt {
  font-family: JB, monospace;
  color: #8b97a3;
  font-size: 18px;
}
dl.kv dd { font-size: 26px; }
dl.kv div.hot { background: rgba(212, 180, 131, 0.14); }
pre.snippet {
  margin-top: 8px;
  font-family: JB, monospace;
  font-size: 22px;
  line-height: 1.55;
  white-space: pre;
  color: #d7dde3;
}
pre.snippet .hotline {
  display: block;
  background: rgba(212, 180, 131, 0.16);
  color: #f4f1ea;
  margin: 0 -12px;
  padding: 0 12px;
}
.center {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  gap: 18px;
}
.rule { width: 128px; height: 3px; background: #d4b483; margin: 8px 0; }
.url { font-size: 44px; letter-spacing: -0.03em; }
.stack { color: #a8b0b8; font-size: 26px; line-height: 1.45; }
.og {
  width: 100%;
  height: 100%;
  padding: 64px 72px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background:
    radial-gradient(800px 480px at 100% 100%, #2a241c 0%, transparent 50%),
    #101418;
}
.og h1 { font-size: 76px; }
.og .url { font-size: 36px; margin-top: 8px; }
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


def problem_slide(sentences: list[str], active: int, py_short: str) -> str:
    items = []
    for index, sentence in enumerate(sentences):
        if index < active:
            kind = "past"
        elif index == active:
            kind = "now"
        else:
            kind = "next"
        items.append(f"<li class=\"{kind}\">{_esc(sentence)}</li>")
    body = f"""
    <div class="dark">
      <header class="top">
        <span class="who">Benjamin Kun</span>
        <span>01 / 05</span>
        <span class="spacer"></span>
        <span>{_clock(0, 10)}</span>
      </header>
      <div class="split">
        <div class="thesis">
          <p class="kicker">The problem</p>
          <h1>Keep the failures visible.</h1>
          <p class="tools">Python {_esc(py_short)}<br>pytest · Playwright<br>page objects</p>
        </div>
        <ol class="beats">{''.join(items)}</ol>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def _status_pill(run: dict[str, Any]) -> str:
    failed = int(run["failed"]) + int(run["errors"])
    if failed:
        return f'<span class="pill fail">{failed} failed</span>'
    return '<span class="pill pass">passed</span>'


def _step(label: str, on: bool) -> str:
    kind = "step on" if on else "step"
    return f'<span class="{kind}">{_esc(label)}</span>'


def report_slide(run: dict[str, Any]) -> str:
    rows = []
    for test in run["tests"]:
        status = test["status"]
        css = "ok" if status == "passed" else "bad"
        rows.append(
            "<tr>"
            f"<td class=\"name\">{_esc(test['name'])}</td>"
            f"<td class=\"{css}\">{_esc(status)}</td>"
            f"<td class=\"num\">{test['time']:.2f}s</td>"
            "</tr>"
        )
    steps = "".join(
        [
            _step("JUnit XML", True),
            '<span class="arrow">→</span>',
            _step("HTML report", True),
            '<span class="arrow">→</span>',
            _step("S3", False),
            '<span class="arrow">→</span>',
            _step("CloudFront", False),
            '<span class="arrow">→</span>',
            _step("Slack link", False),
        ]
    )
    body = f"""
    <div class="paper">
      <header class="top">
        <span class="who">Public sample</span>
        <span>03 / 05</span>
        <span class="spacer"></span>
        <span>Report</span>
      </header>
      <div class="report-title">
        <div>
          <h1>HTML report</h1>
          <p class="sub">From this run's JUnit file. The file stayed on disk.</p>
        </div>
        {_status_pill(run)}
      </div>
      <div class="stats">
        <div class="stat"><b>{_esc(run["python"])}</b><span>interpreter</span></div>
        <div class="stat"><b>{_esc(run["pytest"])}</b><span>pytest</span></div>
        <div class="stat"><b>{_esc(run["playwright"])}</b><span>playwright</span></div>
        <div class="stat"><b>{run["time"]:.2f}s</b><span>junit time</span></div>
      </div>
      <table>
        <thead><tr><th>Test</th><th>Status</th><th class="num">Time</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
      <div class="steps">{steps}</div>
      <p class="note">Target {_esc(run["target"])}. Generated {_esc(run["generated"])}. Serial sample. Publishing through S3 and CloudFront is the framework path, and Slack gets the link. This sample was not uploaded.</p>
    </div>
    """
    return document(body, 1920, 1080)


def dashboard_slide(run: dict[str, Any], focus: str) -> str:
    publish_on = focus == "publish"
    slack_on = focus == "slack"
    steps = "".join(
        [
            _step("JUnit XML", True),
            '<span class="arrow">→</span>',
            _step("HTML report", True),
            '<span class="arrow">→</span>',
            _step("S3", publish_on or slack_on),
            '<span class="arrow">→</span>',
            _step("CloudFront", publish_on or slack_on),
            '<span class="arrow">→</span>',
            _step("Slack link", slack_on),
        ]
    )
    failed = int(run["failed"]) + int(run["errors"])
    passed_css = "ok" if failed == 0 else "bad"
    body = f"""
    <div class="paper">
      <header class="top">
        <span class="who">Public sample</span>
        <span>03 / 05</span>
        <span class="spacer"></span>
        <span>Dashboard</span>
      </header>
      <div class="report-title">
        <div>
          <h1>Dashboard</h1>
          <p class="sub">One local sample run. Counts come from the JUnit file.</p>
        </div>
        {_status_pill(run)}
      </div>
      <div class="dash-nums">
        <div class="big"><b>{run["tests_total"]}</b><span>tests</span></div>
        <div class="big"><b class="{passed_css}">{run["passed"]}</b><span>passed</span></div>
        <div class="big"><b class="{'' if failed == 0 else 'bad'}">{failed}</b><span>failed</span></div>
        <div class="big"><b>{run["time"]:.2f}s</b><span>junit time</span></div>
      </div>
      <div class="steps">{steps}</div>
      <p class="note">No trend and no second run. The framework publishes the HTML report through S3 and CloudFront. Slack gets a link to that report. This sample stayed on disk. {_esc(run["generated"])}.</p>
    </div>
    """
    return document(body, 1920, 1080)


def _node(label: str, caption: str, on: bool) -> str:
    kind = "node on" if on else "node"
    return (
        f'<div class="{kind}"><small>{_esc(caption)}</small>'
        f"<strong>{_esc(label)}</strong></div>"
    )


def _chip(label: str, on: bool) -> str:
    kind = "chip on" if on else "chip"
    return f'<div class="{kind}">{_esc(label)}</div>'


def ci_slide(active: int) -> str:
    # 0 gitlab+k8s, 1 triggers, 2 xdist, 3 lock, 4 totp, 5 api
    body = f"""
    <div class="dark">
      <header class="top">
        <span class="who">Benjamin Kun</span>
        <span>04 / 05</span>
        <span class="spacer"></span>
        <span>{_clock(36, 48)}</span>
      </header>
      <p class="kicker" style="margin-top:36px">CI pipeline</p>
      <h1>Pipeline shape</h1>
      <div class="nodes">
        {_node("Post-deploy", "Trigger", active == 1)}
        {_node("Nightly", "Trigger", active == 1)}
        {_node("GitLab CI", "Job", active in (0, 1))}
        {_node("Kubernetes", "Runs on", active == 0)}
        {_node("pytest-xdist", "Workers", active == 2)}
        {_node("JUnit", "Output", False)}
      </div>
      <div class="chips">
        {_chip("Scarce accounts stay locked", active == 3)}
        {_chip("Login uses TOTP", active == 4)}
        {_chip("API clients do setup", active == 5)}
      </div>
      <p class="disclaimer">A diagram of the framework. This public sample does not run a deploy, a lock, or TOTP.</p>
    </div>
    """
    return document(body, 1920, 1080)


def add_to_cart_lines(source: str) -> list[str]:
    """Dedent the real add_to_cart method so the frame matches the file."""
    start = source.index("    def add_to_cart")
    end = source.index("    def open_cart")
    lines = []
    for line in source[start:end].splitlines():
        if line.startswith("    "):
            line = line[4:]
        lines.append(line.rstrip())
    return [line for line in lines if line.strip()]


def authoring_slide(highlight_wait: bool, lines: list[str]) -> str:
    rendered = []
    for line in lines:
        escaped = _esc(line) if line else " "
        if highlight_wait and "wait_for(state=\"visible\")" in line:
            rendered.append(f'<span class="hotline">{escaped}</span>')
        else:
            rendered.append(escaped)
    state_class = "hot" if highlight_wait else ""
    body = f"""
    <div class="dark">
      <header class="top">
        <span class="who">Benjamin Kun</span>
        <span>05 / 05</span>
        <span class="spacer"></span>
        <span>{_clock(48, 60)}</span>
      </header>
      <p class="kicker" style="margin-top:28px">AI-assisted authoring</p>
      <div class="columns">
        <section class="panel">
          <h2>Chrome DevTools MCP</h2>
          <p class="hint">Structured read from the live page while the check is written.</p>
          <dl class="kv">
            <div><dt>host</dt><dd>practicesoftwaretesting.com</dd></div>
            <div><dt>role</dt><dd>button</dd></div>
            <div><dt>name</dt><dd>Add to cart</dd></div>
            <div class="{state_class}"><dt>state</dt><dd>visible</dd></div>
            <div><dt>test id</dt><dd>add-to-cart</dd></div>
          </dl>
        </section>
        <section class="panel">
          <h2>Page object</h2>
          <p class="hint">video/public_sample/pages.py · visible UI, not a fixed sleep</p>
          <pre class="snippet">{chr(10).join(rendered)}</pre>
        </section>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def end_card(py_short: str) -> str:
    body = f"""
    <div class="dark">
      <header class="top">
        <span class="who">Benjamin Kun</span>
        <span>05 / 05</span>
        <span class="spacer"></span>
        <span>{_clock(48, 60)}</span>
      </header>
      <div class="center">
        <p class="kicker">QA Engineer</p>
        <h1>Benjamin Kun</h1>
        <p class="stack">End-to-end testing</p>
        <div class="rule"></div>
        <p class="url">benikun88.github.io</p>
        <p class="stack">Python {_esc(py_short)} · pytest · Playwright<br>Playwright frames · ffmpeg · edge-tts</p>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def poster_card(py_short: str) -> str:
    body = f"""
    <div class="dark">
      <div class="center">
        <p class="kicker">QA Engineer</p>
        <h1>Benjamin Kun</h1>
        <p class="stack">End-to-end testing</p>
        <div class="rule"></div>
        <p class="url">benikun88.github.io</p>
        <p class="stack">Python {_esc(py_short)} · pytest · Playwright</p>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def og_card(py_short: str) -> str:
    body = f"""
    <div class="og">
      <p class="kicker">QA Engineer</p>
      <h1>Benjamin Kun</h1>
      <p class="stack">End-to-end testing</p>
      <div class="rule"></div>
      <p class="url">benikun88.github.io</p>
      <p class="stack">Python {_esc(py_short)} · pytest · Playwright<br>Page objects · GitLab CI · HTML reports</p>
    </div>
    """
    return document(body, 1200, 630)


def teaser_open() -> str:
    body = """
    <div class="dark">
      <div class="center">
        <p class="kicker">20 second cut</p>
        <h1>End-to-end testing</h1>
        <p class="stack">Benjamin Kun<br>A public practice shop. Synthetic data.</p>
      </div>
    </div>
    """
    return document(body, 1920, 1080)


def snippet_lines_present(source: str) -> None:
    for line in add_to_cart_lines(source):
        if line not in source and ("    " + line) not in source:
            raise SystemExit(f"On-screen snippet is not in pages.py: {line}")
