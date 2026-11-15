import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'text-tool/tools'))
"""Regression checks for alignment padding and real native string entries."""
import unittest
from build import rebuild_block
from translation_project import Project,read_json
from text_codec import ROOT

class FakeProject:
    def __init__(self,target):
        self.segments=[dict(id='rom:000100',words=[0,0x2000,0x2001],source=' テス')]
        self.text=target
    def target(self,s):return self.text

class TextEntryTests(unittest.TestCase):
    @unittest.skipUnless((ROOT/'work/manifest.json').exists(),'Prepare text-tool with the supported original first')
    def test_shop_description_and_ownership_have_real_width_limits(self):
        p=Project()
        self.assertFalse(p.validate())
        p.explicit['asset_361:002C0E']='가'*14
        self.assertIn(('asset_361:002C0E','게임 창의 208픽셀 폭 초과'),p.validate())
        p.explicit['asset_361:002A5E']='가'*9
        self.assertIn(('asset_361:002A5E','게임 창의 128픽셀 폭 초과'),p.validate())
    def test_native_entry_after_padding_starts_at_first_korean_glyph(self):
        b=dict(source='rom',offset=0x100,words=[0,0x2000,0x2001,0xFFFF])
        payload,mapping=rebuild_block(b,FakeProject('저장'),{'저':0x3000,'장':0x3001})
        self.assertEqual(mapping[2],0)
        self.assertEqual(payload[mapping[2]:mapping[2]+2],b'\x30\x00')
        self.assertEqual(mapping[6],4)
    def test_partial_original_keeps_padding_and_offset(self):
        b=dict(source='rom',offset=0x100,words=[0,0x2000,0x2001,0xFFFF])
        payload,mapping=rebuild_block(b,FakeProject(''),{},partial=True)
        self.assertEqual(mapping[2],2)
        self.assertEqual(payload[:2],b'\0\0')
    def test_all_three_real_skipped_padding_entries(self):
        p=Project();blocks=read_json(ROOT/'analysis/selected-blocks.json')
        mapping={c:0x3000+i for i,c in enumerate(sorted({c for s in p.segments for c in p.target(s) if ord(c)>126}))}
        for key in ['rom:0BB406','asset_423:00383E','asset_444:00134A']:
            with self.subTest(key=key):
                s=p.by_id[key];source,off=key.split(':');start=int(off,16)
                b=next(b for b in blocks if b['source']==source and b['offset']<=start<b['end'])
                payload,positions=rebuild_block(b,p,mapping)
                relative=start-b['offset']
                self.assertEqual(s['words'][0],0)
                self.assertEqual(positions[relative],positions[relative+2])
                first=next(c for c in p.target(s) if not c.isspace())
                expected=(mapping[first] if first in mapping else ord(first)-0x20).to_bytes(2,'big')
                self.assertEqual(payload[positions[relative+2]:positions[relative+2]+2],expected)

if __name__=='__main__':unittest.main()
