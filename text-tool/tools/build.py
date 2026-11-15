"""Build the Japanese Legend of Cornell Korean ROM without changing the source."""
import argparse,hashlib,json,struct
from text_codec import ROOT
from translation_project import Project,read_json
from relocate import relocate_references
from extract_rom import compress
from n64_crc import identify,update
from lod_font import encode as encode_glyph,TABLES
from validate_layout import check_page_rows,check_complete_lines

def native_glyph(character):
    from native_font import glyph
    from font_atlas import decode_glyph
    return encode_glyph(decode_glyph(glyph(character)).point(lambda p:144 if p==180 else 180 if p==36 else 0))

def install_font(rom,characters):
    chars=sorted(set(characters));mapping={}
    if len(chars)>881:raise ValueError(f'Native glyph capacity exceeded: {len(chars)}/881')
    # Verified LUI/ADDIU pairs in the native font DMA dispatch function.
    patches=[(0x80CCC,0x80CD0),(0x80D58,0x80D5C),(0x80DE4,0x80DE8),(0x80E70,0x80E74)]
    for bank in range(4):
        while len(rom)%8:rom.append(0)
        base=len(rom);payload=bytearray()
        for i,c in enumerate(chars[bank*256:(bank+1)*256]):
            struct.pack_into('>H',rom,TABLES[0x30+bank][2]+i*2,len(payload))
            payload.extend(native_glyph(c));mapping[c]=0x3000+bank*256+i
        if len(payload)>65535:raise ValueError('Font bank overflows descriptor')
        # DMA reads a full 256-byte window even at the last glyph.
        rom.extend(payload);rom.extend(bytes(256))
        hi,lo=patches[bank];high,low=struct.unpack_from('>I',rom,hi)[0],struct.unpack_from('>I',rom,lo)[0]
        assert high>>26==15 and low>>26==9
        old=((high&65535)<<16)+(low&65535 if low&65535<0x8000 else (low&65535)-65536)
        assert old==TABLES[0x30+bank][1],(bank,hex(old))
        struct.pack_into('>I',rom,hi,high&0xFFFF0000|((base+0x8000)>>16))
        struct.pack_into('>I',rom,lo,low&0xFFFF0000|(base&65535))
    return mapping

def encode(text,mapping):
    words=[]
    for c in text:
        if c=='\n':words.append(0xB600)
        elif c==' ':words.append(0xB700)
        elif c in mapping:words.append(mapping[c])
        elif 0x21<=ord(c)<=0x7e:words.append(ord(c)-0x20)
        else:raise ValueError(('Unmapped target',repr(c)))
    return struct.pack('>'+str(len(words))+'H',*words)

def rebuild_block(b,project,glyphs,partial=False):
    spans={int(s['id'].split(':')[1],16):s for s in project.segments if s['id'].startswith(b['source']+':')}
    out=bytearray();offset_map={};words=b['words'];i=0
    while i<len(words):
        s=spans.get(b['offset']+i*2)
        if s:
            target=project.target(s)
            if not target and not partial:raise ValueError(('Untranslated',s['id']))
            data=encode(target,glyphs) if target else struct.pack('>'+str(len(s['words']))+'H',*s['words'])
            # Some strings begin with an unused zero word for 32-bit alignment.
            # Native callers point AFTER that word (e.g. saving: 800BA808).
            # Translations omit it; preserving its numeric index skipped the
            # first Korean glyph. Map the real text entry to the translation's
            # start, including for the intro prophecy and Henry-help title.
            padding=0
            while target and padding<len(s['words']) and s['words'][padding]==0:padding+=1
            for j in range(len(s['words'])):
                offset_map[i*2+j*2]=len(out)+min(max(0,j-padding)*2,max(0,len(data)-2))
            out.extend(data);i+=len(s['words'])
        else:offset_map[i*2]=len(out);out.extend(struct.pack('>H',words[i]));i+=1
    controls=lambda ws:[w for w in ws if w>=0xA000 and w not in (0xB600,0xB700)]
    assert controls(words)==controls(struct.unpack('>'+str(len(out)//2)+'H',out))
    return out,offset_map

def main(partial=False):
    project=Project();manifest=read_json(ROOT/'work/manifest.json');blocks=read_json(ROOT/'analysis/selected-blocks.json')
    if not partial and project.validate():raise ValueError(project.validate())
    if project.stats()['pending'] and not partial:raise ValueError('Incomplete translation')
    original=(ROOT/'work/original.z64').read_bytes();assert hashlib.sha1(original).hexdigest()=='50439acb5784bea3a4bbba5188c2aeaa1442099d'
    rom=bytearray(original);cic=identify(rom)
    chars=''.join(c for s in project.segments for c in project.target(s) if ord(c)>126)
    glyphs=install_font(rom,chars)
    assets={a['id']:bytearray((ROOT/'work/assets'/a['file']).read_bytes()) for a in manifest['assets']}
    maps={a['id']:bytearray((ROOT/'work/maps'/a['file']).read_bytes()) for a in manifest['maps']}
    surfaces={'rom':rom,**{f'asset_{i:03d}':d for i,d in assets.items()},**{f'map_{i:02d}':d for i,d in maps.items()}}
    changes=[];issues=[];changed_assets=set();changed_maps=set();resident=[]
    for b in blocks:
        data=surfaces[b['source']]
        payload,offset_map=rebuild_block(b,project,glyphs,partial)
        check_page_rows(b['words'],struct.unpack('>'+str(len(payload)//2)+'H',payload),b['id'])
        check_complete_lines(struct.unpack('>'+str(len(payload)//2)+'H',payload),set(glyphs.values()),b['id'])
        old_size=b['end']-b['offset']
        if len(payload)>old_size:issues.append(dict(block=b['id'],reason='Pool exceeds original size',old_size=old_size,new_size=len(payload)));continue
        base=(0x80000000-0xC00 if b['source']=='rom' else manifest['assets'][int(b['source'].split('_')[1])]['vram'] if b['source'].startswith('asset_') else 0x802E3AA0)
        old_base=base+b['offset'];old_end=base+b['end']
        def mapper(v):
            if old_base<=v<old_end:
                delta=v-old_base
                if delta%2:raise ValueError('Odd message pointer')
                return old_base+offset_map[delta]
            return None
        if b['source']=='rom':
            prefix=bytearray(data[:0x124000]);refs,problems=relocate_references(prefix,mapper)
            data[:len(prefix)]=prefix
        else:refs,problems=relocate_references(data,mapper,b['offset'])
        if b['source']=='rom':resident.append((old_base,old_end,offset_map))
        if 'external_pointer' in b:
            ptr=b['external_pointer'];old=struct.unpack_from('>I',rom,ptr)[0]
            assert old==old_base
            refs.append(dict(kind='map_pool',rom_offset=ptr,old=old,new=old_base))
        issues.extend(dict(block=b['id'],**p) for p in problems)
        if not refs:issues.append(dict(block=b['id'],reason='No incoming text reference'))
        data[b['offset']:b['end']]=payload+bytes(old_size-len(payload))
        changes.append(dict(block=b['id'],old_size=old_size,new_size=len(payload),refs=refs))
        if b['source'].startswith('asset_'):changed_assets.add(int(b['source'].split('_')[1]))
        elif b['source'].startswith('map_'):changed_maps.add(int(b['source'].split('_')[1]))
    def common_mapper(v):
        for base,end,offset_map in resident:
            if base<=v<end:return base+offset_map[v-base]
        return None
    for name,data in list(surfaces.items())[1:]:
        refs,problems=relocate_references(data,common_mapper)
        if refs:
            if name.startswith('asset_'):changed_assets.add(int(name.split('_')[1]))
            else:changed_maps.add(int(name.split('_')[1]))
        issues.extend(dict(source=name,**p) for p in problems)
    logo_path=ROOT/'assets/logo/korean-logo-native.png'
    if logo_path.exists():
        from prepare_logo import native_logo,ENGLISH
        from PIL import Image,ImageOps
        logo=Image.open(logo_path).convert('RGBA');assert logo.size==(320,96)
        assert logo.crop(ENGLISH).tobytes()==native_logo(assets[205]).crop(ENGLISH).tobytes()
        for i in range(30):assets[205][i*4096:(i+1)*4096]=ImageOps.flip(logo.crop((i%10*32,i//10*32,i%10*32+32,i//10*32+32))).tobytes()
        changed_assets.add(205)
    report=dict(catalog=project.stats(),glyphs={c:f'{n:04X}' for c,n in glyphs.items()},pools=changes,issues=issues)
    (ROOT/'analysis/build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if issues and not (partial and all(p.get('reason')=='Pool exceeds original size' for p in issues)):
        raise ValueError(f'{len(issues)} unresolved build issues; see analysis/build-report.json')
    for i in sorted(changed_assets):
        while len(rom)%16:rom.append(0)
        start=len(rom);rom.extend(compress(assets[i]));a=manifest['assets'][i]
        struct.pack_into('>II',rom,a['table_offset'],start|0x80000000,len(rom))
        assert len(assets[i])==a['size']
    for i in sorted(changed_maps):
        a=manifest['maps'][i];assert len(maps[i])==a['size'];rom[a['start']:a['end']]=maps[i]
    for lo,hi in [(0xBAC38,0xBAC50),(0xBB124,0xBB138)]:
        assert rom[lo:hi]==original[lo:hi],'Scalar globals adjacent to messages were changed'
    if len(rom)>0x2000000:raise ValueError('ROM exceeds 32 MiB')
    rom.extend(bytes(0x2000000-len(rom)));update(rom,cic)
    output=ROOT/('work/diagnostic.z64' if partial else 'work/korean-candidate.z64');output.write_bytes(rom)
    report.update(output=str(output),rom_sha256=hashlib.sha256(rom).hexdigest(),changed_assets=sorted(changed_assets),changed_maps=sorted(changed_maps))
    (ROOT/'analysis/build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(output=str(output),catalog=project.stats(),changed_assets=len(changed_assets),changed_maps=len(changed_maps)),ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--diagnostic',action='store_true');args=parser.parse_args();main(args.diagnostic)
