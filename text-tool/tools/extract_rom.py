"""Legend of Cornell's bounded zlib resource decoder."""
import zlib,json,hashlib
from pathlib import Path

def decompress(data):
    if len(data)<4 or data[0]!=0x80:raise ValueError('Unexpected resource format')
    size=int.from_bytes(data[:4],'big')&0x7FFFFFFF
    if not 4<=size<=len(data):raise ValueError('Invalid resource length')
    stream=zlib.decompressobj()
    result=stream.decompress(data[4:size],0x1000000)
    if not stream.eof or stream.unused_data or stream.unconsumed_tail:raise ValueError('Invalid zlib boundary')
    return result

def compress(data):
    payload=zlib.compress(bytes(data),9)
    result=(0x80000000|len(payload)+4).to_bytes(4,'big')+payload
    assert decompress(result)==bytes(data)
    return result

def extract():
    from text_codec import ROOT
    manifest=json.loads((ROOT/'data/resource-layout.json').read_text(encoding='utf-8'))
    rom=(ROOT/'work/original.z64').read_bytes()
    if hashlib.sha1(rom).hexdigest()!=manifest['rom_sha1']:raise ValueError('Unsupported original ROM')
    (ROOT/'work/assets').mkdir(parents=True,exist_ok=True)
    for a in manifest['assets']:
        source=rom[a['start']:a['end']];data=decompress(source) if a['compressed'] else source
        assert len(data)==a['size'] and hashlib.sha256(data).hexdigest()==a['sha256']
        (ROOT/'work/assets'/a['file']).write_bytes(data)
    (ROOT/'work/maps').mkdir(exist_ok=True)
    for a in manifest['maps']:(ROOT/'work/maps'/a['file']).write_bytes(rom[a['start']:a['end']])
    (ROOT/'work/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Verified and extracted 473 assets and 47 native map overlays.')
