"""Render the exact 3bpp glyph pixels used by the ROM builder."""
from functools import lru_cache
import struct
from PIL import Image
from text_codec import ROOT
from translation_project import read_json
from font_atlas import decode_glyph
from lod_font import get_glyph
from native_font import glyph

@lru_cache(maxsize=1)
def latin_data():
    manifest=read_json(ROOT/'work/manifest.json')
    assets={i:(ROOT/'work/assets'/manifest['assets'][i]['file']).read_bytes() for i in (199,200)}
    return (ROOT/'work/original.z64').read_bytes(),assets

@lru_cache(maxsize=2048)
def character_image(char):
    if char==' ':return Image.new('RGBA',(8,16))
    if 0x21<=ord(char)<0x7E:
        rom,assets=latin_data();mask=get_glyph(ord(char)-0x20,rom,assets)
        mask=mask.point(lambda p:180 if p==144 else 36 if p==180 else p)
    else:mask=decode_glyph(glyph(char))
    result=Image.new('RGBA',mask.size)
    colors={0:(0,0,0,0),1:(20,15,23,255),2:(60,50,60,255),3:(90,80,90,255),4:(160,150,160,255),5:(243,231,189,255),6:(255,245,214,255),7:(255,255,255,255)}
    result.putdata([colors[min(7,p//36)] for p in mask.getdata()])
    return result

def line_width(text):return sum(character_image(c).width for c in text)

def render(text):
    lines=text.split('\n')
    widths=[line_width(s) for s in lines]
    image=Image.new('RGBA',(max(320,max(widths,default=0)+16),max(96,len(lines)*20+16)),(22,18,28,255))
    for row,line in enumerate(lines):
        x=8
        for char in line:
            im=character_image(char);image.alpha_composite(im,(x,8+row*20));x+=im.width
    return image.convert('RGB'),widths

@lru_cache(maxsize=2048)
def source_glyph(code):
    rom,assets=latin_data()
    mask=get_glyph(code,rom,assets)
    colors={0:(0,0,0,0),1:(66,66,66,255),2:(123,123,123,255),3:(189,189,189,255),4:(255,255,255,255),5:(0,0,0,255)}
    image=Image.new('RGBA',mask.size)
    image.putdata([colors.get(p//36,(255,255,255,255)) for p in mask.getdata()])
    return image

def render_source(words):
    """Read original ROM glyphs directly, without relying on kanji transcription."""
    lines=[[]]
    for code in words:
        if code==0xB600:lines.append([])
        elif code==0xB700:lines[-1].append(Image.new('RGBA',(8,16)))
        elif code<0xA000:lines[-1].append(source_glyph(code))
    widths=[sum(g.width for g in line) for line in lines]
    image=Image.new('RGBA',(max(320,max(widths,default=0)+16),max(96,len(lines)*20+16)),(22,18,28,255))
    for row,line in enumerate(lines):
        x=8
        for glyph_image in line:image.alpha_composite(glyph_image,(x,8+row*20));x+=glyph_image.width
    return image.convert('RGB')
