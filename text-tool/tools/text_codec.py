"""Legend of Cornell text mapping. The original glyph preview is authoritative.

Keep unknown/control words visible. Never silently discard an unknown glyph.
"""
from __future__ import annotations
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[1]

HIRAGANA = "あぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろわをんぁ"
KATAKANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロワヲン"
def character_map() -> dict[int, str]:
    mapping={i:chr(i+0x20) for i in range(0,0x60)}
    mapping.update({0x5F:'◆',0x60:'「',0x61:'」',0x62:'。',0x63:'、',0x64:'ー',0x65:'▶',0x70:'“',0x71:'”',0x72:'∞',0x73:'、'})
    mapping.update({0x66+i:str(i) for i in range(10)})
    mapping.update({0x1000+i:c for i,c in enumerate(HIRAGANA)})
    mapping.update({0x2000+i:c for i,c in enumerate(KATAKANA)})
    mapping[0x2050]='ヴ'
    path=ROOT/'data/kanji.json'
    if path.exists():mapping.update({int(k,16):v for k,v in json.loads(path.read_text(encoding='utf-8')).items()})
    return mapping


CHARACTERS = character_map()


def decode_words(words: list[int]) -> str:
    parts = []
    for w in words:
        if w == 0xB600: parts.append("\n")
        elif w == 0xB700: parts.append(' ')
        elif w == 0xFFFF: parts.append("<PAGE>")
        elif w in CHARACTERS: parts.append(CHARACTERS[w])
        else: parts.append(f"<{w:04X}>")
    return "".join(parts)
