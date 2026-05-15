"""
Regression test: AI was returning ~~## ...~~ headers as active TODO items (2026-05-06).

Verifies that is_active_header() correctly distinguishes active vs closed headers.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from chkp import is_active_header

CASES = [
    ("## Active item", True),
    ("~~## Closed item~~", False),
    ("### Subsection active", True),
    ("~~### Subsection closed~~", False),
    ("~~## ~~Nested strike~~ item~~", False),  # outer ~~ = closed
    ("## ~~partial strike~~ item", True),       # inline strike, header itself active
    ("# Top level active", True),
    ("~~# Top level closed~~", False),
    ("#### Deep heading active", True),
    ("~~#### Deep heading closed~~", False),
    ("Not a header at all", False),
    ("", False),
]


@pytest.mark.parametrize("line,is_active", CASES)
def test_header_status_parsing(line, is_active):
    assert is_active_header(line) == is_active
