#!/usr/bin/env python3
"""Convert a downloaded headshot into the website's portrait format.

Crops the image to a square (biased toward the top, where faces usually are),
resizes it to 320x320, and writes assets/images/people/<id>.webp at no more
than 64 KB. Record the page the photo came from as `photo_source` in
_data/people.yml.

Usage: python3 scripts/normalize_photo.py <person-id> <image-file> [--top 0.15]
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SIZE = 320
MAX_BYTES = 64 * 1024


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("person_id")
    parser.add_argument("image", type=Path)
    parser.add_argument("--top", type=float, default=0.15,
                        help="share of the excess height cropped from the top of portrait images (0 = keep top edge, 0.5 = centre)")
    args = parser.parse_args()

    with Image.open(args.image) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = int((height - side) * args.top) if height > width else 0
    image = image.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)

    for quality in range(85, 40, -5):
        buffer = io.BytesIO()
        image.save(buffer, "WEBP", quality=quality, method=6)
        if buffer.tell() <= MAX_BYTES:
            break
    out = ROOT / "assets" / "images" / "people" / f"{args.person_id}.webp"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(buffer.getvalue())
    print(f"wrote {out.relative_to(ROOT)} ({buffer.tell()} bytes, quality {quality})")


if __name__ == "__main__":
    main()
