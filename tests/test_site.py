import re

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import expect

HEADINGS = (
    "Demo",
    "What I did and how",
    "How I work",
    "Stack",
    "Behind the video",
    "Sample suite",
    "Contact",
)


def test_hero_shows_name_and_title(site):
    expect(site.get_by_role("heading", level=1)).to_have_count(1)
    expect(site.get_by_role("heading", level=1)).to_have_text('Benjamin "Beni" Kun')
    expect(site.get_by_text("QA automation engineer").first).to_be_visible()
    expect(site).to_have_title(re.compile(r"Benjamin \"Beni\" Kun"))


def test_section_headings_are_present(site):
    for name in HEADINGS:
        expect(site.get_by_role("heading", name=name, level=2)).to_be_visible()
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
    expect(site.get_by_role("button", name="0:00–0:10 Problem")).to_have_attribute("data-start", "0")
    expect(site.get_by_role("button", name="0:10–0:22 Live run")).to_have_attribute("data-start", "10")
    expect(site.get_by_role("button", name="0:22–0:36 Reports")).to_have_attribute("data-start", "22")
    expect(site.get_by_role("button", name="0:36–0:48 CI")).to_have_attribute("data-start", "36")
    expect(site.get_by_role("button", name="0:48–1:00 AI-assisted QA")).to_have_attribute(
        "data-start", "48"
    )
    expect(site.get_by_text("Full transcript")).to_be_visible()


def test_profile_links_and_placeholders(site):
    linkedin = site.get_by_role("link", name="LinkedIn", exact=True)
    github = site.get_by_role("link", name="GitHub", exact=True)
    expect(linkedin).to_have_count(2)
    expect(github).to_have_count(2)
    expect(linkedin.first).to_have_attribute("href", "https://www.linkedin.com/in/benjamin-kun")
    expect(github.first).to_have_attribute("href", "https://github.com/benikun88")
    for token in ("{{N_TESTS}}", "{{N_MODULES}}", "{{N_PAGE_OBJECTS}}", "{{CONTACT_EMAIL}}"):
        expect(site.get_by_text(token).first).to_be_visible()
    expect(site.locator('link[rel="canonical"]')).to_have_attribute(
        "href", "https://benikun88.github.io/"
    )
    expect(site.locator('meta[property="og:image"]')).to_have_attribute(
        "content", "https://benikun88.github.io/assets/og-card.png"
    )


def test_poster_and_captions_are_served(page, site_url):
    poster = page.request.get(site_url + "/assets/poster.jpg")
    captions = page.request.get(site_url + "/assets/captions.vtt")
    assert poster.status == 200
    assert captions.status == 200
    assert captions.text().startswith("WEBVTT")


def test_mobile_hero_stays_visible(page, site_url):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(site_url + "/")
    expect(page.get_by_role("heading", level=1)).to_be_visible()
    expect(page.get_by_role("link", name="Watch demo (60 s)")).to_be_visible()
    expect(page.get_by_role("link", name="Sample suite").first).to_be_visible()


def test_no_serious_axe_violations(site):
    results = Axe().run(site)
    serious = [
        item
        for item in results.response["violations"]
        if item.get("impact") in {"serious", "critical"}
    ]
    assert serious == [], results.generate_report()
