# Benjamin "Beni" Kun

Public portfolio for a QA automation engineer. Static HTML, CSS, and vanilla JS. Intended live URL: <https://benikun88.github.io/>.

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

The suite serves this folder on localhost and checks the hero, section headings, video player shell, poster, captions, profile links, and serious or critical axe violations.

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

- `assets/demo.mp4` (H.264, 1920x1080, under 25 MB)
- `assets/demo.webm` (VP9)
- `assets/poster.jpg`
- `assets/captions.vtt`

`poster.jpg` and `captions.vtt` are in the repo. `demo.mp4` and `demo.webm` are produced separately and are not part of this change. The chapter list and the transcript match the planned 60-second narration: problem (0:00), live run on the practice shop (0:10), reports (0:22), CI (0:36), AI-assisted QA and close (0:48).

How the cut is made: an animated HTML and CSS storyboard, frames captured with Playwright and Chromium, encoded with ffmpeg at 1920x1080 in H.264, narrated with edge-tts. The edit went from a 15-second cut to a 20-second cut. The site uses the 60-second cut. The `<video>` element loads the files above from this site.

If an encoded file is larger than 25 MB, switch the player to an unlisted embed on `https://www.youtube-nocookie.com` and leave the video id as an open placeholder. Do not invent the id.

## Sanitization

This site is public. Do not add employer names, internal product names, hostnames, ticket keys, work email addresses, cloud account or bucket names, customer or tenant identifiers, phone numbers, or screenshots from work systems. The demo may record only the public practice shop and this sample suite. Do not paste work code into the sample suite.

Unknowns stay visible as placeholders: `{{CONTACT_EMAIL}}`, `{{N_TESTS}}`, `{{N_MODULES}}`, `{{N_PAGE_OBJECTS}}`. Do not invent numbers or an email address.

## Deploy

`.github/workflows/pages.yml` deploys the static files with GitHub Pages Actions. The repository currently also publishes the `master` branch root. After merge, confirm in the repository settings that Pages is serving the intended build. `.github/workflows/ci.yml` runs the sample suite and the site tests.
