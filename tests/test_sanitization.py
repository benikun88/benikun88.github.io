import base64
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git", "node_modules", ".superdesign", "__pycache__", ".pytest_cache",
    ".venv", ".venv-site", "reports", "test-results", "build",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".mp4", ".webm",
    ".mp3", ".wav", ".woff", ".woff2", ".pdf", ".zip",
}
# This file holds secret-shaped samples for the self-test below.
SKIP_FILES = {"package-lock.json", Path(__file__).name}

# Employer and organization names from the public LinkedIn profile are allowed.
EMPLOYERS = (
    "Via", "Moovit", "SMARTSHOOTER (via Qualitest)", "Scodix", "HOT",
    "IAF - Israeli Air Force", "StartAch",
)

# Encoded so this file does not trip its own scan. Work domains and email
# addresses, names that are not on the profile, and two work details that are
# deliberately left off the site.
_BLOCKED_SUBSTRINGS = ("cmlkZXdpdGh2aWE=", "QXRlcmE=", "c21hcnQgd2VhcG9uIHNpZ2h0")
_BLOCKED_WORDS = ("Um9iaW4=",)
_BLOCKED_PATTERNS = ("XGJFXHMqLVxzKjEwNlxi",)

ALLOWED_EMAILS = {"benikun88@gmail.com", "customer@practicesoftwaretesting.com"}
ALLOWED_KEYS = {"UTF-8", "SHA-256"}

RULES = {
    "ticket key": re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d+\b"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    "cloud account id": re.compile(r"\b\d{12}\b|arn:aws:[a-z0-9-]+:[a-z0-9-]*:\d{12}"),
    "bucket": re.compile(r"s3://[a-z0-9.-]+|[a-z0-9.-]+\.s3[.-][a-z0-9.-]*amazonaws\.com", re.I),
    "internal host": re.compile(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:internal|corp|intra|intranet|lan)\b", re.I),
    "phone number": re.compile(r"\+972[\d\s-]{8,}|\b0[5-9]\d-?\d{7}\b"),
}


def _decode(items):
    return [base64.b64decode(item).decode() for item in items]


def findings(text):
    found = []
    lowered = text.lower()
    for term in _decode(_BLOCKED_SUBSTRINGS):
        if term.lower() in lowered:
            found.append(f"blocked term #{_decode(_BLOCKED_SUBSTRINGS).index(term) + 1}")
    for term in _decode(_BLOCKED_WORDS):
        if re.search(rf"\b{re.escape(term)}\b", text, re.I):
            found.append("blocked word")
    for pattern in _decode(_BLOCKED_PATTERNS):
        if re.search(pattern, text):
            found.append("omitted work detail")
    for label, rule in RULES.items():
        for match in rule.findall(text):
            value = match if isinstance(match, str) else match[0]
            if label == "ticket key" and value in ALLOWED_KEYS:
                continue
            if label == "email" and value.lower() in ALLOWED_EMAILS:
                continue
            found.append(f"{label}: {value}")
    return found


def public_files():
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_file() or SKIP_DIRS.intersection(relative.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES or path.name in SKIP_FILES:
            continue
        yield path


def test_repository_has_no_secrets():
    problems = {}
    for path in public_files():
        hits = findings(path.read_text(encoding="utf-8", errors="ignore"))
        if hits:
            problems[str(path.relative_to(ROOT))] = hits
    assert problems == {}


def test_employer_names_are_allowed_and_shown():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    for name in EMPLOYERS:
        assert findings(name) == []
        assert name in page


@pytest.mark.parametrize(
    "sample",
    [
        "PROJ-123",
        "someone@" + _decode(_BLOCKED_SUBSTRINGS)[0] + ".com",
        "dev@company.io",
        "account 123456789012",
        "s3://team-artifacts",
        "api.staging.internal",
        "+972 52 123 4567",
        _decode(_BLOCKED_SUBSTRINGS)[1],
        _decode(_BLOCKED_WORDS)[0],
    ],
)
def test_check_still_blocks_secrets(sample):
    assert findings(sample) != []
