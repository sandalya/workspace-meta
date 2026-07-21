#!/usr/bin/env python3
"""chkp summarize client - runs INSIDE the sandbox, imported by chkp.

Call request_finalize(project) after write_pending() has already put the
checkpoint request on disk. It sends ONLY {"project": "<id>"} over the
socket - no prompt, no key, no content. The daemon reads the actual
what_done/next_step/context from the pending file it already trusts (same
project dir the sandboxed agent already has write access to).

Best-effort: if the broker is down it returns an error dict instead of
raising, so a checkpoint is never lost - the pending file stays on disk and
can be replayed with `chkp-sumd.py --once <project>`.
"""
from __future__ import annotations
import json, os, socket

DEFAULT_SOCK = os.path.expanduser("~/.openclaw/run/chkp-sumd.sock")


def request_finalize(project: str, sock_path: str = DEFAULT_SOCK,
                      timeout: float = 180.0) -> dict:
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall((json.dumps({"project": project}) + "\n").encode())
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()
        return json.loads(data.decode().strip())
    except Exception as e:
        return {"ok": False, "detail": f"broker unreachable: {e}"}


if __name__ == "__main__":
    import sys
    pid = sys.argv[1] if len(sys.argv) > 1 else "drone-recon"
    print(json.dumps(request_finalize(pid), indent=2))
