"""
Tests for prompt caching behavior in chkp.

Unit tests: verify that cache_control blocks are structured correctly.
Integration tests (require ANTHROPIC_API_KEY): verify actual cache_r > 0 on 2nd call.

Run unit tests only:
  cd meta && python3 -m pytest chkp/tests/test_prompt_caching.py -v -k "not integration"

Run all (including real API calls):
  cd meta && python3 -m pytest chkp/tests/test_prompt_caching.py -v
"""

import json
import sys
import os
import urllib.request
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import chkp

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

SAMPLE_WARM = """\
---
project: test
updated: 2026-05-01
---
# WARM

## Auth module

```yaml
last_touched: 2026-05-01
tags: [auth]
status: active
```

JWT-based auth. See auth.py.

## Config system

```yaml
last_touched: 2026-04-20
tags: [config]
status: active
```

YAML config with startup validation.
"""

SAMPLE_COLD = """\
---
project: test
updated: 2026-05-01
---
# COLD

## 2026-04-01: Old session auth

```yaml
archived_at: 2026-04-01
reason: Replaced by JWT
tags: [auth, legacy]
```

Session-based auth removed.
"""

SAMPLE_MEMORY = "# MEMORY\n\nProject: test\nRules: keep it simple.\n"


def _make_fake_response(cache_r=0, cache_w=0, content="[]"):
    """Build a fake urllib response for call_anthropic."""
    response_data = {
        "content": [{"type": "text", "text": content}],
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 10,
            "cache_read_input_tokens": cache_r,
            "cache_creation_input_tokens": cache_w,
        },
    }
    encoded = json.dumps(response_data).encode("utf-8")

    class FakeResponse:
        def read(self):
            return encoded
        def __enter__(self):
            return self
        def __exit__(self, *_):
            pass

    return FakeResponse()


# ──────────────────────────────────────────────
# Unit tests: cache_control structure
# ──────────────────────────────────────────────

def test_call_anthropic_sets_cache_control_on_large_cacheable(monkeypatch):
    """When cacheable prefix > 1024 estimated tokens, user[0] gets cache_control."""
    captured_payload = {}

    def fake_urlopen(req, timeout):
        captured_payload["body"] = json.loads(req.data.decode("utf-8"))
        return _make_fake_response(cache_w=5000)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    large_text = "x " * 3000  # ~3000 tokens estimated
    chkp.call_anthropic("fake_key", chkp.MODEL_HAIKU, "sys", large_text, "volatile")

    body = captured_payload["body"]
    user_content = body["messages"][0]["content"]
    assert user_content[0].get("cache_control") == {"type": "ephemeral"}, \
        "First user block should have cache_control when >= 1024 tokens"


def test_call_anthropic_no_cache_control_on_small_cacheable(monkeypatch):
    """When cacheable prefix < 1024 estimated tokens, no cache_control added."""
    captured_payload = {}

    def fake_urlopen(req, timeout):
        captured_payload["body"] = json.loads(req.data.decode("utf-8"))
        return _make_fake_response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    small_text = "small"  # < 1024 tokens
    chkp.call_anthropic("fake_key", chkp.MODEL_HAIKU, "sys", small_text, "volatile")

    body = captured_payload["body"]
    user_content = body["messages"][0]["content"]
    # Should be a single merged block (no cache_control)
    assert len(user_content) == 1
    assert "cache_control" not in user_content[0]


def test_system_prompt_has_cache_control(monkeypatch):
    """System block always has cache_control set."""
    captured_payload = {}

    def fake_urlopen(req, timeout):
        captured_payload["body"] = json.loads(req.data.decode("utf-8"))
        return _make_fake_response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    chkp.call_anthropic("fake_key", chkp.MODEL_HAIKU, "sys_prompt", "small", "volatile")

    body = captured_payload["body"]
    system = body["system"]
    assert isinstance(system, list)
    assert system[0]["cache_control"] == {"type": "ephemeral"}



def test_system_prompt_token_estimate_exceeds_minimum():
    """SYSTEM_PROMPT should be long enough to meet the 1024-token minimum for caching."""
    estimated_tokens = len(chkp.SYSTEM_PROMPT) // chkp._CHARS_PER_TOKEN
    assert estimated_tokens >= chkp._CACHE_MIN_TOKENS, (
        f"SYSTEM_PROMPT estimated {estimated_tokens} tokens, "
        f"need >= {chkp._CACHE_MIN_TOKENS} for system-level caching"
    )


# ──────────────────────────────────────────────
# Integration tests (real API calls)
# ──────────────────────────────────────────────

def _get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    workspace = Path.home() / ".openclaw" / "workspace"
    for env_path in [workspace / "insilver-v3" / ".env", workspace / ".env"]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip("'\"")
                    if val:
                        return val
    return ""


@pytest.mark.integration
def test_integration_main_call_writes_cache():
    """First main-call chkp should produce cache_creation_input_tokens > 0."""
    api_key = _get_api_key()
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not available")

    import tempfile, os
    usage = {}
    original_call = chkp.call_anthropic

    def capturing_call(*args, **kwargs):
        result = original_call(*args, **kwargs)
        # Parse usage from the last printed line (call_anthropic prints it)
        return result

    # Use a small cacheable to minimise cost — just enough to exceed 1024 tokens
    cacheable = ("test content " * 400)  # ~5200 chars ≈ 1300 tokens
    volatile = "Project: test\nWhat done: minimal test run for caching verification."

    captured_usage = {}

    def fake_urlopen(req, timeout):
        body = json.loads(req.data.decode("utf-8"))
        # Forward to real API
        real_resp_data = None
        real_req = urllib.request.Request(
            req.full_url, data=req.data, headers=dict(req.headers), method="POST"
        )
        with urllib.request.urlopen(real_req, timeout=timeout) as resp:
            real_resp_data = json.loads(resp.read().decode("utf-8"))
        usage_data = real_resp_data.get("usage", {})
        captured_usage["cache_w"] = usage_data.get("cache_creation_input_tokens", 0)
        captured_usage["cache_r"] = usage_data.get("cache_read_input_tokens", 0)

        # Re-wrap as fake response
        class WrappedResp:
            def read(self):
                return json.dumps(real_resp_data).encode("utf-8")
            def __enter__(self):
                return self
            def __exit__(self, *_):
                pass
        return WrappedResp()

    with patch.object(urllib.request, "urlopen", side_effect=fake_urlopen):
        chkp.call_anthropic(api_key, chkp.MODEL_HAIKU, chkp.SYSTEM_PROMPT, cacheable, volatile, max_tokens=50)

    assert captured_usage.get("cache_w", 0) > 0, \
        f"Expected cache_creation_input_tokens > 0, got {captured_usage}"


