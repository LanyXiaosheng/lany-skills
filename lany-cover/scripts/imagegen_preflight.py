#!/usr/bin/env python3
"""Check the local proxy and ChatGPT image endpoint without credentials."""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


def port_open(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def endpoint_status(proxy: str, timeout: float) -> tuple[bool, str]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    request = urllib.request.Request(
        "https://chatgpt.com/backend-api/codex/images/edits",
        method="GET",
        headers={"User-Agent": "lany-imagegen-preflight/1.0"},
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        if error.code in {401, 403, 404, 405}:
            return True, f"HTTP {error.code} (reachable; authentication or method expected)"
        if error.code == 407:
            return False, "HTTP 407 (proxy authentication failed)"
        if error.code == 429:
            return False, "HTTP 429 (remote reachable but currently rate limited)"
        if 500 <= error.code <= 599:
            return False, f"HTTP {error.code} (upstream unavailable)"
        return False, f"HTTP {error.code} (unexpected preflight response)"
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight the Lany image generation network path")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7897)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--open-clash", action="store_true")
    args = parser.parse_args()
    if not port_open(args.host, args.port, min(args.timeout, 3.0)):
        if args.open_clash and sys.platform == "darwin":
            subprocess.run(["open", "-a", "Clash Verge"], check=False)
            deadline = time.monotonic() + min(max(args.timeout, 3.0), 15.0)
            while time.monotonic() < deadline:
                if port_open(args.host, args.port, 0.5):
                    break
                time.sleep(0.5)
        if not port_open(args.host, args.port, 1.0):
            print(f"FAIL proxy {args.host}:{args.port} is not listening")
            return 2
    proxy = f"http://{args.host}:{args.port}"
    ok, detail = endpoint_status(proxy, args.timeout)
    if not ok:
        print(f"FAIL proxy is listening but endpoint handshake failed: {detail}")
        return 3
    print(f"OK proxy={proxy} endpoint={detail}; handshake only, upload not proven")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
