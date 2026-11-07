import hashlib
import re
from pathlib import Path

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import expect

HEADINGS = {
    "about": "More than finding bugs.",
    "work": "Proof of how I think.",
    "demo": "Ninety seconds of the work.",
    "experience": "Built through experience.",
    "stack": "The toolkit.",
    "sample-suite": "A public sample suite.",
    "hobbies": "Hobbies.",
    "contact": "Got a complex problem? I'm in.",
}


def test_hero_shows_name_and_title(site):
    expect(site.get_by_role("heading", level=1)).to_have_count(1)
    expect(site.get_by_role("heading", level=1)).to_have_text(
        re.compile(r"Breaking\s*things\.\s*Building\s*confidence\.")
    )
    hero = site.locator(".hero-desc")
    expect(hero).to_contain_text('Benjamin "Beni" Kun')
    expect(hero).to_contain_text("Senior QA & Automation Engineer")
    expect(site).to_have_title(re.compile(r"Benjamin \"Beni\" Kun"))


def test_section_headings_are_present(site):
    for section, name in HEADINGS.items():
        heading = site.locator(f"#{section} h2")
        expect(heading).to_be_visible()
        expect(heading).to_have_text(re.compile(r"\s*".join(map(re.escape, name.split()))))
    expect(site.get_by_role("main")).to_be_visible()
    expect(site.get_by_role("banner")).to_be_visible()
    expect(site.get_by_role("contentinfo")).to_be_visible()


def test_video_player_shell(site):
    video = site.locator("video")
    expect(video).to_have_attribute("preload", "metadata")
    expect(video).to_have_attribute("poster", "assets/poster.jpg")
    expect(site.get_by_role("group", name="Playback")).to_be_visible()
    expect(site.get_by_role("button", name="Play")).to_be_visible()
    expect(site.get_by_role("slider", name="Seek")).to_be_visible()
    expect(video.locator("source").nth(0)).to_have_attribute("src", "assets/demo.mp4")
    expect(video.locator("source").nth(0)).to_have_attribute("type", "video/mp4")
    expect(video.locator("source").nth(1)).to_have_attribute("src", "assets/demo.webm")
    expect(video.locator("source").nth(1)).to_have_attribute("type", "video/webm")
    track = video.locator("track")
    expect(track).to_have_attribute("src", "assets/captions.vtt")
    expect(track).to_have_attribute("kind", "captions")
    expect(site.get_by_role("button", name="0:00–0:06 Intro")).to_have_attribute("data-start", "0")
    expect(site.get_by_role("button", name="0:06–0:20 Experience")).to_have_attribute("data-start", "6")
    expect(site.get_by_role("button", name="0:20–0:32 Tools")).to_have_attribute("data-start", "20")
    expect(site.get_by_role("button", name="0:32–0:52 Automation dashboard")).to_have_attribute("data-start", "32")
    expect(site.get_by_role("button", name="0:52–1:06 Parallel-safe framework")).to_have_attribute("data-start", "52")
    expect(site.get_by_role("button", name="1:06–1:16 Live run")).to_have_attribute("data-start", "66")
    expect(site.get_by_role("button", name="1:16–1:26 AI-assisted authoring and CI")).to_have_attribute("data-start", "76")
    expect(site.get_by_role("button", name="1:26–1:28 Also shipped")).to_have_attribute("data-start", "86")
    expect(site.get_by_role("button", name="1:28–1:30 End card")).to_have_attribute("data-start", "88")
    expect(site.get_by_text("Full transcript")).to_be_visible()


def test_profile_and_contact_links(site):
    linkedin = site.locator('a[href="https://www.linkedin.com/in/benjamin-kun"]')
    github = site.locator('a[href="https://github.com/benikun88"]')
    email = site.locator('a[href^="mailto:benikun88@gmail.com"]')
    expect(linkedin).to_have_count(2)
    expect(github).to_have_count(3)
    expect(site.get_by_role("link", name="LinkedIn profile")).to_be_visible()
    expect(site.get_by_role("link", name="GitHub profile")).to_be_visible()
    expect(site.get_by_role("link", name="Say hello")).to_have_attribute(
        "href", re.compile(r"^mailto:benikun88@gmail\.com")
    )
    assert email.count() >= 3
    expect(site.get_by_text("{{")).to_have_count(0)
    expect(site.locator('link[rel="canonical"]')).to_have_attribute(
        "href", "https://benikun88.github.io/"
    )
    expect(site.locator('meta[property="og:image"]')).to_have_attribute(
        "content", "https://benikun88.github.io/assets/og-card.png"
    )


def test_assets_are_requested_by_content_hash(site):
    root = Path(__file__).resolve().parents[1]
    for selector, attribute, name in (
        ('link[rel="stylesheet"]', "href", "styles.css"),
        ("script[src]", "src", "script.js"),
    ):
        digest = hashlib.sha256((root / name).read_bytes()).hexdigest()[:8]
        actual = site.locator(selector).get_attribute(attribute)
        assert actual == f"{name}?v={digest}", "run `npm run build` after changing styles or script"


def test_poster_and_captions_are_served(page, site_url):
    poster = page.request.get(site_url + "/assets/poster.jpg")
    captions = page.request.get(site_url + "/assets/captions.vtt")
    assert poster.status == 200
    assert captions.status == 200
    assert captions.text().startswith("WEBVTT")


def test_theme_toggle_switches_mode(site):
    toggle = site.get_by_role("button", name=re.compile(r"mode", re.I))
    expect(toggle).to_be_visible()
    before = site.locator("html").get_attribute("data-theme")
    toggle.click()
    after = site.locator("html").get_attribute("data-theme")
    assert before in {"light", "dark"}
    assert after in {"light", "dark"}
    assert before != after
    expect(toggle).to_have_attribute("aria-label", re.compile(before))
    expect(site.locator("#stack h2")).to_be_visible()


def test_showcase_filter_and_modal(site):
    cards = site.locator(".project")
    expect(cards).to_have_count(6)
    site.get_by_role("button", name="AI workflows").click()
    expect(site.get_by_role("button", name="AI workflows")).to_have_attribute("aria-pressed", "true")
    expect(cards.filter(visible=True)).to_have_count(1)
    site.get_by_role("button", name="All work").click()
    expect(cards.filter(visible=True)).to_have_count(6)

    cards.first.get_by_role("button", name="Explore approach").click()
    dialog = site.get_by_role("dialog")
    expect(dialog).to_be_visible()
    expect(dialog.get_by_role("heading")).to_have_text("End-to-end automation")
    expect(dialog.get_by_role("listitem")).to_have_count(3)
    expect(site.get_by_role("button", name="Close dialog")).to_be_focused()
    site.keyboard.press("Escape")
    expect(dialog).to_be_hidden()


def test_career_timeline_and_credentials(site):
    expect(site.locator(".career")).to_have_count(6)
    expect(site.locator(".career-date").first).to_have_text("JUN 2024 — PRESENT")
    expect(site.get_by_text("B.Sc. Computer Science")).to_be_visible()
    expect(site.get_by_text("Holon Institute of Technology")).to_be_visible()
    for language in ("Hebrew", "Romanian", "English"):
        expect(site.locator(".extras").get_by_text(language)).to_be_visible()


def test_mobile_hero_stays_visible(page, site_url):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(site_url + "/")
    expect(page.get_by_role("heading", level=1)).to_be_visible()
    expect(page.get_by_role("link", name="Watch the reel (90 s)")).to_be_visible()
    width = page.evaluate("document.documentElement.scrollWidth")
    assert width <= 390
    menu = page.get_by_role("button", name="Menu")
    expect(menu).to_be_visible()
    menu.click()
    expect(menu).to_have_attribute("aria-expanded", "true")
    page.get_by_role("navigation", name="Sections").get_by_role("link", name="Experience").click()
    expect(menu).to_have_attribute("aria-expanded", "false")


def test_no_serious_axe_violations(site):
    results = Axe().run(site)
    serious = [
        item
        for item in results.response["violations"]
        if item.get("impact") in {"serious", "critical"}
    ]
    assert serious == [], results.generate_report()
