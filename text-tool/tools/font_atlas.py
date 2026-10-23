"""Decode the frozen intermediate Korean three-bit glyphs."""
from pathlib import Path
import json
import struct
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def decode_glyph(data: bytes, bit_offset: int = 0) -> Image.Image:
    if bit_offset:
        data = ((int.from_bytes(data, "big") << bit_offset) & ((1 << (len(data) * 8)) - 1)).to_bytes(len(data), "big")
    height, width = data[:2]
    if not 0 < height <= 16 or not 0 < width <= 16:
        raise ValueError((height, width))
    bits = int.from_bytes(data[2:2 + (height * width * 3 + 7) // 8], "big")
    padding = (-height * width * 3) % 8
    values = [((bits >> (padding + (height * width - i - 1) * 3)) & 7) * 36
              for i in range(height * width)]
    im = Image.new("L", (width, height))
    im.putdata(values)
    return im
