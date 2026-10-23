"""Independently check final ROM resource integrity and preservation rules."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from text_codec import ROOT
from translation_project import Project,read_json
from extract_rom import decompress
from n64_crc import identify,update
from prepare_logo import native_logo,ENGLISH
from build import rebuild_block

def main():
    manifest=read_json(ROOT/'work/manifest.json');report=read_json(ROOT/'analysis/build-report.json')
    original=(ROOT/'work/original.z64').read_bytes();rom=Path(report['output']).read_bytes()
    assert len(rom)==0x2000000 and hashlib.sha256(rom).hexdigest()==report['rom_sha256']
    checked=bytearray(rom);update(checked,identify(rom));assert bytes(checked)==rom
    assets={}
    for a in manifest['assets']:
        start,end=struct.unpack_from('>II',rom,a['table_offset']);flag=start>>31;start&=0x7FFFFFFF
        assert 0<=start<=end<=len(rom)
        data=decompress(rom[start:end]) if flag else rom[start:end]
        vram,finish=struct.unpack_from('>II',rom,manifest['vram_table']+a['id']*8)
        assert vram==a['vram'] and finish-vram==len(data)==a['size']
        if a['id'] not in report['changed_assets']:assert hashlib.sha256(data).hexdigest()==a['sha256']
        assets[a['id']]=data
    maps={}
    for a in manifest['maps']:
        assert struct.unpack_from('>II',rom,a['table_offset'])==(a['start'],a['end'])
        data=rom[a['start']:a['end']];maps[a['id']]=data
        if a['id'] not in report['changed_maps']:assert data==original[a['start']:a['end']]
    project=Project();assert not project.validate() and not project.stats()['pending']
    glyphs={c:int(code,16) for c,code in report['glyphs'].items()}
    surfaces={'rom':rom,**{f'asset_{i:03d}':d for i,d in assets.items()},**{f'map_{i:02d}':d for i,d in maps.items()}}
    blocks=read_json(ROOT/'analysis/selected-blocks.json')
    for b in blocks:
        expected,_=rebuild_block(b,project,glyphs)
        data=surfaces[b['source']][b['offset']:b['end']]
        assert data==expected+bytes(len(data)-len(expected)),b['id']
    oldlogo=(ROOT/'work/assets'/manifest['assets'][205]['file']).read_bytes()
    newlogo=native_logo(assets[205]);oldimage=native_logo(oldlogo)
    assert newlogo.tobytes()==Image.open(ROOT/'assets/logo/korean-logo-native.png').convert('RGBA').tobytes()
    assert newlogo.crop(ENGLISH).tobytes()==oldimage.crop(ENGLISH).tobytes()
    assert assets[205][30*4096:]==oldlogo[30*4096:]
    assert assets[199]==(ROOT/'work/assets'/manifest['assets'][199]['file']).read_bytes()
    for lo,hi in ((0xBAC38,0xBAC50),(0xBB124,0xBB138)):
        assert original[lo:hi]==rom[lo:hi]
    # All source data between resident code and the original font banks is exact.
    # This includes the native sound banks, samples and sequence tables.
    lo,hi=0x124000,0x7FF040
    assert original[lo:hi]==rom[lo:hi]
    # Original compressed assets and everything after raw map overlays is kept.
    assert original[0x8E0950:]==rom[0x8E0950:len(original)]
    result=dict(sha256=report['rom_sha256'],rom=report['output'],size=len(rom),cic=identify(rom),
        translation=project.stats(),text_pools=len(blocks),asset_count=len(assets),map_count=len(maps),
        changed_assets=len(report['changed_assets']),changed_maps=len(report['changed_maps']),
        all_resources_decompress_and_match_native_sizes=True,all_translated_pools_match_project=True,
        control_sequences_and_english_runs_preserved=True,n64_checksum_valid=True,
        english_font_pixels_preserved=True,english_title_pixels_preserved=True,
        other_title_graphics_preserved=True,resident_scalar_globals_preserved=True,
        preserved_native_sound_region=[lo,hi],sound_region_sha256=hashlib.sha256(rom[lo:hi]).hexdigest(),
        original_compressed_payload_region_preserved=True,space_width_pixels=8)
    (ROOT/'analysis/release-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
