"""Pack localized lettering into native tiles; retain the English subtitle."""
from pathlib import Path
import json,shutil
from PIL import Image,ImageOps
from text_codec import ROOT
ENGLISH=(178,75,320,96)
GENERATED=ROOT/'assets/logo/korean-lettering-imagegen.png'

def native_logo(data):
    im=Image.new('RGBA',(320,96))
    for i in range(30):im.paste(ImageOps.flip(Image.frombytes('RGBA',(32,32),bytes(data[i*4096:(i+1)*4096]))),(i%10*32,i//10*32))
    return im

def main():
    folder=ROOT/'assets/logo';source=folder/'korean-lettering-imagegen.png'
    if not source.exists():raise FileNotFoundError('Missing included Korean lettering image')
    metadata=json.loads((ROOT/'work/manifest.json').read_text());data=(ROOT/'work/assets'/metadata['assets'][205]['file']).read_bytes()
    original=native_logo(data);result=Image.open(source).convert('RGBA').resize((320,96),Image.Resampling.LANCZOS)
    result.paste(original.crop(ENGLISH),ENGLISH[:2]);assert result.crop(ENGLISH).tobytes()==original.crop(ENGLISH).tobytes()
    result.save(folder/'korean-logo-native.png')
    (folder/'generation.txt').write_text('Built-in image_gen. Text-localization of the original Japanese title. Exact Korean: 악마성 드라큘라 / 묵시록 외전. Keep transparent background, red beveled lettering and original demonic emblems. English LEGEND OF CORNELL and TM pixels restored from source ROM during tile packing.\n',encoding='utf-8')

if __name__=='__main__':main()
