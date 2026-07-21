#!/usr/bin/env python3
"""chkp push client - runs INSIDE the sandbox, imported by chkp.

Call request_push(repo_id) right after your existing commit step. It is
best-effort: if the broker is down it returns an error dict instead of raising,
so a checkpoint is never lost just because push is unavailable.
"""
from __future__ import annotations
import json, os, socket

DEFAULT_SOCK = os.path.expanduser("~/.openclaw/run/chkp-pushd.sock")


def request_push(repo_id: str, sock_path: str = DEFAULT_SOCK,
                 timeout: float = 15.0) -> dict:
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall((json.dumps({"repo": repo_id}) + "\n").encode())
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
    rid = sys.argv[1] if len(sys.argv) > 1 else "riko"
    print(json.dumps(request_push(rid), indent=2))
