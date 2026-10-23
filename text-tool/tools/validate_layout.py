"""Check page rows against the original native window allocation."""
from functools import lru_cache

@lru_cache(maxsize=2048)
def original_width(word):
    from native_preview import latin_data
    from lod_font import get_glyph
    rom,assets=latin_data()
    return get_glyph(word,rom,assets).width

def lines(words,glyphs=None):
    result=[];line=[];width=0
    for index,word in enumerate(words):
        if word==0xB600 or word in (0xB200,0xFFFF,0xB500) or word>>8 in (0xAD,0xAE,0xAF,0xAA):
            if line:result.append((index,width,line))
            line=[];width=0
        elif word==0xB700:line.append(word);width+=8
        elif word<0xA000:
            line.append(word);width+=16 if glyphs and word in glyphs else original_width(word)
    return result

def check_complete_lines(words,korean_codes,block_id):
    for end,width,line in lines(words,korean_codes):
        if width>240:raise ValueError(f'{block_id}: complete timed line ending at word {end} is {width}px (limit 240)')

def page_rows(words):
    rows=[];count=1
    for word in words:
        if word==0xB600:count+=1
        if word in (0xB200,0xFFFF,0xB500):rows.append(count);count=1
    return rows

def check_page_rows(original,target,block_id):
    before,after=page_rows(original),page_rows(target)
    if len(before)!=len(after):raise ValueError(f'{block_id}: page boundary mismatch')
    for i,(old,new) in enumerate(zip(before,after)):
        if new>max(4,old):raise ValueError(f'{block_id} page {i}: {new} rows exceed native window ({max(4,old)})')
