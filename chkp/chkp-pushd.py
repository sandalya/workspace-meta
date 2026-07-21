#!/usr/bin/env python3
"""chkp-pushd - host-side git push broker for chkp.

Runs OUTSIDE Claude Code's bwrap sandbox as a `systemd --user` service.

Why it exists: an SSH-remote `git push` cannot run from inside CC's sandbox
(network isolation blocks port 22). chkp still writes memory + commits INSIDE
the sandbox; this daemon performs the push on the host, where SSH and the key
are available.

Protocol: the client (inside the sandbox) sends exactly {"repo": "<repo_id>"}.
It sends nothing else - no path, no remote, no branch, no flags. The daemon
resolves all of that itself from its own config. That is the security boundary:
the socket is same-user (0600), so socket perms do NOT stop a prompt-injected
agent - only the daemon-side validation below does. This mirrors CC's own git
proxy, which validates repo/branch before attaching credentials.

Usage:
  chkp-pushd.py                # run daemon (foreground; systemd wraps it)
  chkp-pushd.py --pin          # fill pinned_url for every repo from its remote
  chkp-pushd.py --test <repo>  # perform one push as if requested (host check)
"""
from __future__ import annotations
import json, os, socket, socketserver, subprocess, sys, threading, time
from pathlib import Path
from datetime import datetime

CONFIG = Path(__file__).with_name("chkp-pushd.config.json")


def expand(p) -> Path:
    return Path(os.path.expanduser(str(p)))


def load_cfg() -> dict:
    return json.loads(CONFIG.read_text())


def log(cfg: dict, msg: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    try:
        lp = expand(cfg["log"])
        lp.parent.mkdir(parents=True, exist_ok=True)
        with lp.open("a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def git(path, *args, cfg: dict):
    """Run git with an explicit, non-interactive SSH command so the daemon
    never depends on an ssh-agent being present in the systemd user session."""
    env = dict(os.environ)
    key = expand(cfg["ssh_key"])
    env["GIT_SSH_COMMAND"] = (
        f"ssh -i {key} -o IdentitiesOnly=yes -o BatchMode=yes "
        f"-o StrictHostKeyChecking=accept-new"
    )
    return subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True, text=True, env=env, timeout=120,
    )


def current_branch(path, cfg) -> str | None:
    r = git(path, "rev-parse", "--abbrev-ref", "HEAD", cfg=cfg)
    return r.stdout.strip() if r.returncode == 0 else None


def remote_url(path, remote, cfg) -> str | None:
    r = git(path, "remote", "get-url", remote, cfg=cfg)
    return r.stdout.strip() if r.returncode == 0 else None


_last: dict[str, float] = {}          # repo_id -> last push ts (rate limiting)
_lock = threading.Lock()


def handle_request(repo_id: str, cfg: dict) -> dict:
    repos = cfg["repos"]
    if repo_id not in repos:
        return {"ok": False, "detail": f"repo '{repo_id}' not in allowlist"}
    spec = repos[repo_id]
    path = expand(spec["path"])
    remote = spec.get("remote", "origin")

    with _lock:
        now = time.time()
        if now - _last.get(repo_id, 0) < cfg.get("rate_limit_sec", 5):
            return {"ok": False, "detail": "rate-limited"}
        _last[repo_id] = now

    if not (path / ".git").exists():
        return {"ok": False, "detail": f"{path} is not a git repo"}

    # Verify the remote is who we expect (blocks push-to-attacker-remote).
    url = remote_url(path, remote, cfg)
    pinned = spec.get("pinned_url")
    if pinned and url != pinned:
        return {"ok": False,
                "detail": f"remote url mismatch (got {url!r}, pinned {pinned!r})"}
    if not pinned:
        log(cfg, f"WARN {repo_id}: pinned_url is null - run `--pin` to lock it")

    # Only push the current branch (or an allowlisted one).
    branch = current_branch(path, cfg)
    if not branch or branch == "HEAD":
        return {"ok": False, "detail": "detached HEAD or unknown branch"}
    allow = spec.get("branches") or []
    if allow and branch not in allow:
        return {"ok": False, "detail": f"branch '{branch}' not allowed"}

    # Plain push is fast-forward-only; we NEVER pass --force.
    r = git(path, "push", remote, branch, cfg=cfg)
    ok = r.returncode == 0
    tail = ((r.stderr or r.stdout).strip().splitlines() or [""])[-1]
    log(cfg, f"push {repo_id} {branch} -> {'OK' if ok else 'FAIL'} :: {tail}")
    return {"ok": ok, "detail": tail, "repo": repo_id, "branch": branch}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        cfg = self.server.cfg
        try:
            raw = self.rfile.readline().decode().strip()
            req = json.loads(raw) if raw.startswith("{") else {"repo": raw}
            repo_id = str(req.get("repo", "")).strip()
            resp = handle_request(repo_id, cfg)
        except Exception as e:
            resp = {"ok": False, "detail": f"bad request: {e}"}
        self.wfile.write((json.dumps(resp) + "\n").encode())


class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True

    def __init__(self, sock_path: str, cfg: dict):
        self.cfg = cfg
        if os.path.exists(sock_path):
            os.unlink(sock_path)
        super().__init__(sock_path, Handler)
        os.chmod(sock_path, 0o600)


def run_daemon():
    cfg = load_cfg()
    sock = expand(cfg["socket"])
    sock.parent.mkdir(parents=True, exist_ok=True)
    log(cfg, f"chkp-pushd starting on {sock}")
    Server(str(sock), cfg).serve_forever()


def cmd_pin():
    cfg = load_cfg()
    for rid, spec in cfg["repos"].items():
        url = remote_url(expand(spec["path"]), spec.get("remote", "origin"), cfg)
        spec["pinned_url"] = url
        print(f"pinned {rid}: {url}")
    CONFIG.write_text(json.dumps(cfg, indent=2))


def cmd_test(repo_id: str):
    print(json.dumps(handle_request(repo_id, load_cfg()), indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_daemon()
    elif sys.argv[1] == "--pin":
        cmd_pin()
    elif sys.argv[1] == "--test" and len(sys.argv) == 3:
        cmd_test(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(2)
