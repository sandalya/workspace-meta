"""
Tests that PROMPT.md is included in the git commit and not written again after.

The regression: copy_to_clipboard() was writing PROMPT.md AFTER git_commit_push(),
leaving it dirty in the working tree.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import chkp
from chkp import copy_to_clipboard, git_commit_push, write_file


@pytest.fixture
def mini_git_repo(tmp_path):
    """Minimal git repo with a PROMPT.md file, committed."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)
    # Initial commit so the repo is non-empty
    (tmp_path / "README.md").write_text("init")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "--no-verify", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def git_status_porcelain(repo_dir):
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_prompt_md_committed(mini_git_repo, monkeypatch):
    """After git_commit_push, PROMPT.md must be in the commit, not dirty."""
    prompt_content = "Проект: test\nThis is the prompt."
    prompt_path = mini_git_repo / "PROMPT.md"
    write_file(str(prompt_path), prompt_content)

    git_commit_push(str(mini_git_repo), "chkp(test): done")

    status = git_status_porcelain(mini_git_repo)
    assert status == "", f"Working tree dirty after commit: {status!r}"


def test_copy_to_clipboard_does_not_write_prompt(mini_git_repo, monkeypatch):
    """copy_to_clipboard must NOT write PROMPT.md (to avoid post-commit dirty state)."""
    prompt_content = "Проект: test\nPrompt content"
    prompt_path = mini_git_repo / "PROMPT.md"
    write_file(str(prompt_path), prompt_content)

    # Commit PROMPT.md
    git_commit_push(str(mini_git_repo), "chkp(test): include prompt")
    assert git_status_porcelain(mini_git_repo) == ""

    # Simulate copy_to_clipboard call (DISPLAY not set → returns False, but must not write)
    monkeypatch.delenv("DISPLAY", raising=False)
    copy_to_clipboard(prompt_content, str(mini_git_repo))

    # Tree must still be clean
    status = git_status_porcelain(mini_git_repo)
    assert status == "", f"copy_to_clipboard dirtied the tree: {status!r}"
