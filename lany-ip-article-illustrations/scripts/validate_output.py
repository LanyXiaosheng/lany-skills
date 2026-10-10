#!/usr/bin/env python3
"""Validate final dimensions and reject a dominant white background."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        width, height = int(width_text), int(height_text)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("size must look like 1500x600") from error
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a final Lany image")
    parser.add_argument("image")
    parser.add_argument("--size", type=parse_size, required=True)
    parser.add_argument("--max-light-fraction", type=float, default=0.45)
    parser.add_argument("--background", choices=("white", "transparent", "dark"), default="white")
    args = parser.parse_args()
    path = Path(args.image).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"missing image: {path}")
    with Image.open(path) as image:
        if args.background == "transparent" and "A" not in image.getbands():
            print("FAIL missing-alpha-channel")
            return 4
        rgb = image.convert("RGB")
        if rgb.size != args.size:
            print(f"FAIL size={rgb.size[0]}x{rgb.size[1]} expected={args.size[0]}x{args.size[1]}")
            return 2
        sample = rgb.copy()
        sample.thumbnail((256, 256))
        pixels = list(sample.getdata())
        light = sum(1 for red, green, blue in pixels if red >= 235 and green >= 235 and blue >= 235)
        fraction = light / max(len(pixels), 1)
        if args.background == "dark" and fraction > args.max_light_fraction:
            print(f"FAIL near-white-fraction={fraction:.3f} max={args.max_light_fraction:.3f}")
            return 3
    print(f"OK background={args.background} size={args.size[0]}x{args.size[1]} near-white-fraction={fraction:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
