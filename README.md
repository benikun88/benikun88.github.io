# Benjamin "Beni" Kun

Public portfolio for a QA automation engineer. HTML, Sass, and vanilla JS. Intended live URL: <https://benikun88.github.io/>.

Styles live in `scss/` and compile to `styles.css`. Dark is the default theme; the header button switches to light and remembers the choice. Fonts (DM Sans, DM Mono, Space Grotesk, SIL Open Font License) are self-hosted in `assets/fonts/`, so the page makes no third-party requests.

```bash
npm install
npm run build
```

`npm run build` compiles the Sass and stamps `index.html` with a content hash for `styles.css` and `script.js` (`styles.css?v=…`). GitHub Pages lets browsers cache those files for 10 minutes, so without the stamp a visitor can get new HTML with an old stylesheet. Commit the stamped `index.html`; a site test fails if the stamp is stale.

## Run the site

From the repository root:

```bash
python3 -m http.server 8080
```

Open <http://127.0.0.1:8080/>.

## Site tests

Python 3.13.

```bash
python3.13 -m venv .venv-site
. .venv-site/bin/activate
python -m pip install -r tests/requirements.txt
python -m playwright install chromium
python -m pytest tests
```

The suite serves this folder on localhost and checks the hero, section headings, video player shell, poster, captions, profile and email links, the theme toggle, showcase filters and dialog, the career timeline, the mobile menu, and serious or critical axe violations.

## Sample suite

UI and API checks against the public practice shop at <https://practicesoftwaretesting.com/>. The catalog is synthetic. Do not point these tests at any other host.

```bash
cd sample-suite
python3.13 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest
```

The shop refuses headless Chromium. On a machine with a display, `python -m pytest` is enough if the suite launches a headed browser (it does). On Linux CI, use:

```bash
xvfb-run -a python -m pytest
```

pytest writes:

- `sample-suite/reports/junit.xml`
- `sample-suite/reports/report.html`

CI uploads those files as the `sample-suite-report` artifact. They are not committed, and they are not published under `/reports/latest/`, so a third-party shop outage does not block the site deploy.

## Demo video

The player on the home page expects files in this repository:

- `assets/demo.mp4` (H.264, 1280x720 web cut)
- `assets/demo.webm` (VP9)
- `assets/poster.jpg`
- `assets/captions.vtt`

All four are in the repo; `video/` holds the pipeline that renders them. The chapter list and the transcript match the 90-second showreel: Intro (0:00), Experience (0:06), Tools (0:20), Automation dashboard (0:32), Parallel-safe framework (0:52), Live run (1:06), AI-assisted authoring and CI (1:16), Also shipped (1:26), End card (1:28).

How the cut is made: an animated HTML and CSS storyboard, frames captured with Playwright and Chromium, encoded with ffmpeg in H.264, narrated with edge-tts. The 1920x1080 master stays outside the repo. The `<video>` element loads the files above from this site.

If an encoded file is larger than 25 MB, switch the player to an unlisted embed on `https://www.youtube-nocookie.com` and leave the video id as an open placeholder. Do not invent the id.

## Sanitization

This site is public. Employer and organization names are shown exactly as they appear on the public LinkedIn profile (<https://www.linkedin.com/in/benjamin-kun>): Via, StartAch (volunteer), Moovit, SMARTSHOOTER (via Qualitest), Scodix, HOT, and IAF - Israeli Air Force. Do not add anything else from work: internal product or project names, internal hostnames or URLs, ticket keys, work email addresses, cloud account IDs or bucket names, customer, city, or tenant identifiers, phone numbers, or screenshots, dashboards, or code from work systems. The demo may record only the public practice shop and this sample suite.

`tests/test_sanitization.py` scans every text file in the repository for those patterns, plus the remaining blocked names, work domains, and work details that are deliberately left off the site. It also checks that the employer names above pass. `video/render.py` applies the same blocked-term list to the video sources.

Unknowns stay visible as placeholders: `{{CONTACT_EMAIL}}`, `{{N_TESTS}}`, `{{N_MODULES}}`, `{{N_PAGE_OBJECTS}}`. Do not invent numbers or an email address.

## Deploy

`.github/workflows/pages.yml` deploys the static files with GitHub Pages Actions. The repository currently also publishes the `master` branch root. After merge, confirm in the repository settings that Pages is serving the intended build. `.github/workflows/ci.yml` runs the sample suite and the site tests.
