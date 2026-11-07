"""Synthetic dashboard figures for the showreel.

Fixed seed. Invented test names. These numbers are not a real run.
"""

from __future__ import annotations

import random

SEED = 20261107
SAMPLE_GATE = 0.90
TESTS = (
    "test_home_catalog",
    "test_search_filters",
    "test_sort_price",
    "test_add_to_cart",
    "test_cart_total",
    "test_stock_state",
)
ENVS = ("dev", "staging", "prod")
DAYS = tuple(f"Day {index}" for index in range(1, 8))


def build_sample() -> dict:
    rng = random.Random(SEED)
    matrix: dict[str, dict[str, list[str]]] = {}
    daily = {day: {"pass": 0, "fail": 0, "skip": 0} for day in DAYS}
    for test in TESTS:
        matrix[test] = {}
        for env in ENVS:
            row: list[str] = []
            for day in DAYS:
                roll = rng.random()
                if roll < 0.07:
                    status = "skip"
                elif roll < 0.24:
                    status = "fail"
                else:
                    status = "pass"
                row.append(status)
                daily[day][status] += 1
            matrix[test][env] = row

    passed = sum(bucket["pass"] for bucket in daily.values())
    failed = sum(bucket["fail"] for bucket in daily.values())
    skipped = sum(bucket["skip"] for bucket in daily.values())
    attempted = passed + failed
    rate = (passed / attempted) if attempted else 0.0

    flaky: list[dict] = []
    broken: list[dict] = []
    for test in TESTS:
        cells = [status for env in ENVS for status in matrix[test][env]]
        fails = cells.count("fail")
        passes = cells.count("pass")
        latest = [matrix[test][env][-1] for env in ENVS]
        if fails and passes:
            flaky.append({"name": test, "fails": fails, "kind": "flaky"})
        elif fails and not passes:
            broken.append({"name": test, "fails": fails, "kind": "broken"})
        elif all(item == "fail" for item in latest) and fails:
            broken.append({"name": test, "fails": fails, "kind": "broken"})
    flaky.sort(key=lambda item: item["fails"], reverse=True)
    ranked = (flaky + broken)[:4]

    return {
        "seed": SEED,
        "gate": SAMPLE_GATE,
        "tests": TESTS,
        "envs": ENVS,
        "days": DAYS,
        "matrix": matrix,
        "daily": [{"day": day, **daily[day]} for day in DAYS],
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "rate": rate,
        "above_gate": rate >= SAMPLE_GATE,
        "ranked": ranked,
    }
