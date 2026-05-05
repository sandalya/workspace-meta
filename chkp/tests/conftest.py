"""
Shared helpers for chkp integration tests.

Functions:
  load_fixture(name)   — load 5 files from fixtures/<name>/
  run_chkp_dry(fixture) — invoke chkp.py --dry-run in isolated tmpdir, return parsed dict
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
CHKP_PY = TESTS_DIR.parent / "chkp.py"
REAL_WORKSPACE = Path.home() / ".openclaw" / "workspace"


def _read_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # Try real project .env — same logic as chkp.load_api_key
    for env_path in [
        REAL_WORKSPACE / "insilver-v3" / ".env",
        REAL_WORKSPACE / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip("'\"")
                    if val:
                        return val
    raise RuntimeError("ANTHROPIC_API_KEY not found — set env var or ensure insilver-v3/.env exists")


def load_fixture(name: str) -> dict:
    d = FIXTURES_DIR / name
    return {
        "hot": (d / "input_hot.md").read_text(encoding="utf-8"),
        "warm": (d / "input_warm.md").read_text(encoding="utf-8"),
        "cold": (d / "input_cold.md").read_text(encoding="utf-8"),
        "session": json.loads((d / "input_session.json").read_text(encoding="utf-8")),
        "expected": json.loads((d / "expected.json").read_text(encoding="utf-8")),
    }


def _extract_json(stdout: str) -> dict:
    """Find the last top-level JSON object in stdout."""
    decoder = json.JSONDecoder()
    lines = stdout.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("{"):
            candidate = "\n".join(lines[i:])
            try:
                obj, _ = decoder.raw_decode(candidate)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                pass
    raise ValueError(f"No JSON dict found in chkp stdout.\nstdout[:1000]:\n{stdout[:1000]}")


def run_chkp_dry(fixture: dict) -> dict:
    """Run chkp --dry-run in isolated tmpdir. Returns parsed JSON dict."""
    api_key = _read_api_key()
    session = fixture["session"]

    with tempfile.TemporaryDirectory(prefix="chkp_test_") as tmpdir:
        tmpdir = Path(tmpdir)

        proj_dir = tmpdir / "insilver-v3"
        proj_dir.mkdir()
        (proj_dir / "HOT.md").write_text(fixture["hot"], encoding="utf-8")
        (proj_dir / "WARM.md").write_text(fixture["warm"], encoding="utf-8")
        (proj_dir / "COLD.md").write_text(fixture["cold"], encoding="utf-8")

        meta_chkp = tmpdir / "meta" / "chkp"
        meta_chkp.mkdir(parents=True)
        (meta_chkp / "projects.yaml").write_text(
            "insilver-v3:\n"
            "  dir: insilver-v3\n"
            "  env_file: insilver-v3/.env\n"
            "  service: insilver-v3\n",
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["CHKP_WORKSPACE"] = str(tmpdir)
        env["ANTHROPIC_API_KEY"] = api_key

        result = subprocess.run(
            [
                sys.executable, str(CHKP_PY),
                "--dry-run", "insilver-v3",
                session["done"],
                session["next"],
                session["context"],
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=180,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"chkp --dry-run exited {result.returncode}\n"
                f"--- stdout ---\n{result.stdout}\n"
                f"--- stderr ---\n{result.stderr}"
            )

        return _extract_json(result.stdout)


def extract_now_section(hot_text: str) -> str:
    """Return content of ## Now section (stripped)."""
    m = re.search(r"## Now\n+(.*?)(?=\n## |\Z)", hot_text, re.DOTALL)
    return m.group(1).strip() if m else ""
