#!/usr/bin/env python3
"""Unit tests for prompt caching logic in chkp.py."""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO

sys.path.insert(0, os.path.dirname(__file__))
from chkp import build_user_prompt, call_anthropic, _CACHE_MIN_TOKENS, _CHARS_PER_TOKEN


DUMMY_KEY = "sk-ant-test-key"
DUMMY_MODEL = "claude-haiku-4-5-20251001"
DUMMY_SYSTEM = "You are a memory manager."

# ~5000 chars of WARM content → estimated ~1250 tokens → above threshold
BIG_WARM = "x" * (_CACHE_MIN_TOKENS * _CHARS_PER_TOKEN + 100)
SMALL_WARM = "tiny warm"  # well below 1024 tokens


def _mock_response(cache_w=100, cache_r=0):
    body = json.dumps({
        "content": [{"type": "text", "text": '{"hot":"h","warm":"w","cold_append":"","prompt":"p"}'}],
        "usage": {
            "input_tokens": 500,
            "output_tokens": 80,
            "cache_creation_input_tokens": cache_w,
            "cache_read_input_tokens": cache_r,
        },
        "stop_reason": "end_turn",
    }).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestBuildUserPrompt(unittest.TestCase):
    def _call(self, warm=BIG_WARM, cold="cold", memory="mem"):
        return build_user_prompt(
            project="testproj",
            what_done="did stuff",
            next_step="do more",
            context="ctx",
            hot="hot content",
            warm=warm,
            cold=cold,
            memory=memory,
            today="2026-05-04",
        )

    def test_returns_tuple_of_two_strings(self):
        result = self._call()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        cacheable, volatile = result
        self.assertIsInstance(cacheable, str)
        self.assertIsInstance(volatile, str)

    def test_cacheable_contains_warm_cold_memory(self):
        cacheable, _ = self._call()
        self.assertIn("Current WARM.md", cacheable)
        self.assertIn("Current COLD.md", cacheable)
        self.assertIn("MEMORY.md", cacheable)

    def test_volatile_contains_session_and_hot(self):
        _, volatile = self._call()
        self.assertIn("did stuff", volatile)
        self.assertIn("do more", volatile)
        self.assertIn("Current HOT.md", volatile)
        self.assertIn("hot content", volatile)

    def test_volatile_does_not_contain_warm(self):
        _, volatile = self._call(warm="unique_warm_marker_xyz")
        self.assertNotIn("unique_warm_marker_xyz", volatile)

    def test_no_memory_omits_memory_section(self):
        cacheable, _ = self._call(memory=None)
        self.assertNotIn("MEMORY.md", cacheable)


class TestCallAnthropicCacheControl(unittest.TestCase):
    def _captured_payload(self, cacheable, volatile):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["data"] = json.loads(req.data.decode("utf-8"))
            captured["headers"] = dict(req.headers)
            return _mock_response()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            call_anthropic(DUMMY_KEY, DUMMY_MODEL, DUMMY_SYSTEM, cacheable, volatile)

        return captured

    def test_large_prefix_sets_cache_control_on_cacheable_block(self):
        info = self._captured_payload(BIG_WARM, "volatile part")
        payload = info["data"]

        # system must be a list with cache_control
        self.assertIsInstance(payload["system"], list)
        self.assertEqual(payload["system"][0]["cache_control"], {"type": "ephemeral"})

        # user content must be two blocks
        content = payload["messages"][0]["content"]
        self.assertEqual(len(content), 2)

        # first block (cacheable) must have cache_control
        self.assertIn("cache_control", content[0])
        self.assertEqual(content[0]["cache_control"], {"type": "ephemeral"})
        self.assertIn(BIG_WARM, content[0]["text"])

        # second block (volatile) must NOT have cache_control
        self.assertNotIn("cache_control", content[1])
        self.assertIn("volatile part", content[1]["text"])

    def test_small_prefix_sends_monolithic_without_cache_control(self):
        info = self._captured_payload(SMALL_WARM, "volatile part")
        payload = info["data"]

        content = payload["messages"][0]["content"]
        self.assertEqual(len(content), 1, "Small prefix → should be single monolithic block")
        self.assertNotIn("cache_control", content[0])
        self.assertIn(SMALL_WARM, content[0]["text"])
        self.assertIn("volatile part", content[0]["text"])

    def test_beta_header_present(self):
        info = self._captured_payload(BIG_WARM, "v")
        header_keys = {k.lower() for k in info["headers"]}
        self.assertIn("anthropic-beta", header_keys)

    def test_safeguard_boundary(self):
        # exactly at threshold: len = 1024 * 4 → estimated = 1024 → should cache
        at_threshold = "a" * (_CACHE_MIN_TOKENS * _CHARS_PER_TOKEN)
        info = self._captured_payload(at_threshold, "v")
        content = info["data"]["messages"][0]["content"]
        self.assertEqual(len(content), 2)

        # one char below: len = 1024*4 - 1 → estimated = 1023 → no cache
        below = "a" * (_CACHE_MIN_TOKENS * _CHARS_PER_TOKEN - 1)
        info2 = self._captured_payload(below, "v")
        content2 = info2["data"]["messages"][0]["content"]
        self.assertEqual(len(content2), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
