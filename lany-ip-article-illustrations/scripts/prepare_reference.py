#!/usr/bin/env python3
"""Create a non-destructive lightweight PNG reference with macOS sips."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a lightweight image-generation reference")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--max-long-side", type=int, default=384)
    args = parser.parse_args()
    source = Path(args.input).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"missing input: {source}")
    if args.max_long_side < 128 or args.max_long_side > 1024:
        raise SystemExit("--max-long-side must be between 128 and 1024")
    output.parent.mkdir(parents=True, exist_ok=True)
    sips = shutil.which("sips")
    if not sips:
        raise SystemExit("sips is required on this macOS workflow")
    subprocess.run(
        [sips, "-Z", str(args.max_long_side), str(source), "--out", str(output)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
