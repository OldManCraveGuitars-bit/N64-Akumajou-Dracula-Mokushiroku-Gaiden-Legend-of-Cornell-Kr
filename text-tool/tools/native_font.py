"""Render frozen Korean glyphs in an intermediate 16 x 16 three-bit format."""
from pathlib import Path
import struct
import hashlib,json
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageChops
from text_codec import ROOT

FONT = Path("C:/Windows/Fonts/gulim.ttc")


@lru_cache(maxsize=1)
def frozen_glyphs():
    folder=ROOT/'assets/font'
    if not (folder/'manifest.json').exists():return {}
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    data=(folder/'native-glyphs.bin').read_bytes()
    assert hashlib.sha256(data).hexdigest()==manifest['sha256']
    assert len(data)==len(manifest['characters'])*98
    return {c:data[i*98:(i+1)*98] for i,c in enumerate(manifest['characters'])}

def glyph(character: str) -> bytes:
    cached=frozen_glyphs().get(character)
    if cached is not None:return cached
    mask = Image.new("L", (16, 16))
    draw = ImageDraw.Draw(mask)
    font = ImageFont.truetype(str(FONT), 15)
    draw.text((0, 0), character, font=font, fill=255, stroke_width=0)
    mask = mask.point(lambda p: 255 if p >= 112 else 0)
    shadow = Image.new("L", (16, 16))
    shadow.paste(mask.crop((0,0,15,15)),(1,1))
    value = 0
    for foreground, background in zip(mask.getdata(),shadow.getdata()):
        value = (value << 3) | (5 if foreground else 1 if background else 0)
    return b"\x10\x10" + value.to_bytes(96, "big")
