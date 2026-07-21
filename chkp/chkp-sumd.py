#!/usr/bin/env python3
"""chkp-sumd - host-side checkpoint-finalize broker for chkp.

Runs OUTSIDE Claude Code's bwrap sandbox as a `systemd --user` service.

Why it exists: chkp's finalize step needs ANTHROPIC_API_KEY to summarize a
session into HOT/WARM/COLD memory, but the sandbox denies reading .env /
secrets on purpose (anti-exfil for a project that scrapes untrusted data).
So the in-sandbox chkp writes the raw session inputs to a pending file and
does a local git commit of whatever it can (nothing secret); this daemon
does everything that needs the key: the Anthropic call, applying warm_ops,
writing HOT/WARM/COLD, the backlog flags, the memory commit, and the push
(chained through the existing chkp-pushd machinery via chkp.py's own
git_commit_push()).

Protocol: the client (inside the sandbox) sends exactly {"project": "<id>"}.
Nothing else - no prompt, no key, no path, no content. That is the security
boundary: the socket is same-user (0600), so socket perms do NOT stop a
prompt-injected agent - only project-allowlist + rate-limit + daily cap
below do. Worst case for a compromised agent: it can trigger processing of
pending checkpoints it already wrote to its own project dir - capped,
logged, revocable.

Usage:
  chkp-sumd.py                  # run daemon (foreground; systemd wraps it)
  chkp-sumd.py --once <project> # process pending once, no socket (cron/manual)
  chkp-sumd.py --test <project> # alias for --once, prints the JSON response
"""
from __future__ import annotations
import json, os, socket, socketserver, sys, threading, time
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chkp  # noqa: E402  (reuses SYSTEM_PROMPT, run_checkpoint_finalize, warm/backlog logic)

if os.environ.get("CHKP_SUMD_MOCK") == "1":
    def _mock_call_anthropic(api_key, model, system_prompt, cacheable, volatile,
                             max_tokens=16000, timeout=300):
        return json.dumps({
            "hot": (
                "---\nproject: mock\nupdated: " + date.today().isoformat() + "\n---\n"
                "# HOT\n\n## Now\n[MOCK] finalize round-trip test.\n\n"
                "## Last done\n- mock\n\n## Next\nmock\n\n## Blockers\nNone."
            ),
            "warm_ops": [],
            "cold_append": "",
        })
    chkp.call_anthropic = _mock_call_anthropic  # module-global lookup, so run_checkpoint_finalize picks it up too

CONFIG = Path(__file__).with_name("chkp-sumd.config.json")


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


_last: dict[str, float] = {}          # project -> last trigger ts (rate limiting)
_lock = threading.Lock()


def _cap_path(cfg: dict) -> Path:
    return expand(cfg.get("cap_state", "~/.openclaw/logs/chkp-sumd.cap.json"))


def _load_cap_state(cfg: dict) -> dict:
    p = _cap_path(cfg)
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def _reserve_cap(cfg: dict, n: int) -> tuple[bool, int]:
    """Reserve n calls against today's cap. Returns (allowed, remaining_before)."""
    p = _cap_path(cfg)
    today = date.today().isoformat()
    with _lock:
        state = _load_cap_state(cfg)
        if state.get("date") != today:
            state = {"date": today, "count": 0}
        cap = cfg.get("daily_call_cap", 200)
        remaining = cap - state["count"]
        if n > remaining:
            return False, remaining
        state["count"] += n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state))
        return True, remaining


def _pending_dir(project: str) -> Path:
    return Path(chkp.PENDING_DIR) / project


def handle_request(project: str, cfg: dict) -> dict:
    projects = chkp.load_projects()
    if project not in projects:
        return {"ok": False, "detail": f"project '{project}' not in allowlist"}

    with _lock:
        now = time.time()
        if now - _last.get(project, 0) < cfg.get("rate_limit_sec", 5):
            return {"ok": False, "detail": "rate-limited"}
        _last[project] = now

    pending_dir = _pending_dir(project)
    if not pending_dir.is_dir():
        return {"ok": True, "detail": "no pending", "processed": 0}
    files = sorted(f for f in pending_dir.iterdir() if f.suffix == ".json")
    if not files:
        return {"ok": True, "detail": "no pending", "processed": 0}

    allowed, remaining = _reserve_cap(cfg, len(files))
    if not allowed:
        return {"ok": False, "detail": f"daily call cap reached (remaining {remaining}, need {len(files)})"}

    api_key = os.environ.get(cfg["api_key_env"])
    if not api_key:
        return {"ok": False, "detail": f"{cfg['api_key_env']} not set in daemon environment"}

    done_dir = pending_dir / "done"
    failed_dir = pending_dir / "failed"

    project_cfg = projects[project]
    details = []
    ok_overall = True
    for f in files:
        try:
            payload = json.loads(f.read_text())
            result = chkp.run_checkpoint_finalize(project, project_cfg, payload, api_key)
            details.append(f"{f.name}: {result['detail']}")
            done_dir.mkdir(parents=True, exist_ok=True)
            f.rename(done_dir / f.name)
        except Exception as e:
            ok_overall = False
            details.append(f"{f.name}: FAILED — {e}")
            failed_dir.mkdir(parents=True, exist_ok=True)
            try:
                f.rename(failed_dir / f.name)
            except Exception:
                pass
            log(cfg, f"ERROR processing {project}/{f.name}: {e}")

    detail = " | ".join(details)
    log(cfg, f"finalize {project}: processed={len(files)} ok={ok_overall} :: {detail[:300]}")
    return {"ok": ok_overall, "detail": detail, "project": project, "processed": len(files)}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        cfg = self.server.cfg
        try:
            raw = self.rfile.readline().decode().strip()
            req = json.loads(raw) if raw.startswith("{") else {"project": raw}
            project = str(req.get("project", "")).strip()
            resp = handle_request(project, cfg)
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
    log(cfg, f"chkp-sumd starting on {sock}")
    Server(str(sock), cfg).serve_forever()


def cmd_once(project: str):
    print(json.dumps(handle_request(project, load_cfg()), indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_daemon()
    elif sys.argv[1] in ("--once", "--test") and len(sys.argv) == 3:
        cmd_once(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(2)
