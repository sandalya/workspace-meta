"""
Regression tests for chkp.py HOT.md ## Now hallucinations.

Each fixture captures a real failure: chkp Haiku wrote yesterday's WARM/HOT
facts into the new ## Now instead of summarising the current session's `done`.

Fixtures:
  2026-05-05_morning — voice integration session (commit c6704d5 hallucinated)
  2026-05-05_evening — Etap 4 Ed coverage session (commit 07bfa5b hallucinated)

Run (baseline expects FAIL on both):
  cd meta && python3 -m pytest chkp/tests/test_no_hallucination.py -v
"""

import pytest
from .conftest import load_fixture, run_chkp_dry, extract_now_section

FIXTURES = [
    "2026-05-05_morning",
    "2026-05-05_evening",
    "2026-05-05_meta_chkp_evals",
]


@pytest.mark.parametrize("fixture_name", FIXTURES)
def test_now_section_no_hallucination(fixture_name):
    fixture = load_fixture(fixture_name)
    result = run_chkp_dry(fixture)

    hot_text = result.get("hot", "")
    assert hot_text, f"[{fixture_name}] result['hot'] is empty"

    now = extract_now_section(hot_text)
    assert now, f"[{fixture_name}] ## Now section not found in HOT.md output"

    expected = fixture["expected"]
    now_lower = now.lower()

    missing = [
        phrase for phrase in expected["must_contain_in_now"]
        if phrase.lower() not in now_lower
    ]
    ghost = [
        phrase for phrase in expected["must_NOT_contain_in_now"]
        if phrase.lower() in now_lower
    ]

    failures = []
    if missing:
        failures.append(f"MISSING from ## Now: {missing}")
    if ghost:
        failures.append(f"GHOST (should NOT be in ## Now): {ghost}")

    if failures:
        sep = "\n" + "=" * 60 + "\n"
        pytest.fail(
            f"\n[{fixture_name}]{sep}"
            + "\n".join(failures)
            + f"{sep}## Now content:\n{now}"
        )
