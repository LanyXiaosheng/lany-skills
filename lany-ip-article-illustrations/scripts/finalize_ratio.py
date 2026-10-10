#!/usr/bin/env python3
"""Crop and resize a generated source image into a non-destructive final PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("size must look like 1500x600") from error
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize an image at an exact size")
    parser.add_argument("source")
    parser.add_argument("output")
    parser.add_argument("--size", type=parse_size, required=True)
    parser.add_argument("--focal-x", type=float, default=0.5)
    parser.add_argument("--focal-y", type=float, default=0.5)
    args = parser.parse_args()
    if not 0 <= args.focal_x <= 1 or not 0 <= args.focal_y <= 1:
        raise SystemExit("focal coordinates must be between 0 and 1")
    source = Path(args.source).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"missing source: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        mode = "RGBA" if "A" in image.getbands() else "RGB"
        final = ImageOps.fit(
            image.convert(mode),
            args.size,
            method=Image.Resampling.LANCZOS,
            centering=(args.focal_x, args.focal_y),
        )
        final.save(output, format="PNG", optimize=True)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
