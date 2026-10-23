"""Native nibble RLE font format, verified against the game's 80080464 decoder."""
import struct
from pathlib import Path
from PIL import Image

TABLES={0:(199,0,0xBA160,128),0x10:(200,0,0xBA320,80),0x20:('rom',0x7FF040,0xBA260,96),
        0x30:('rom',0x800790,0xBA3C0,256),0x31:('rom',0x807C60,0xBA5C0,256),
        0x32:('rom',0x80F0B0,0xBA7C0,256),0x33:('rom',0x816400,0xBA9C0,113)}

def decode(data,offset=0):
    width=16-(data[offset+1]>>4);height=16-(data[offset+1]&15)
    nibbles=[n for b in data[offset+2:offset+256] for n in (b>>4,b&15)]
    pixels=[];prev=255;pos=0
    while len(pixels)<width*height:
        value=nibbles[pos];pos+=1
        if value==prev:
            count=nibbles[pos];pos+=1
            pixels.extend([value]*(15 if count==0 else count-1));prev=255
        else:pixels.append(value);prev=value
        if len(pixels)>width*height:raise ValueError('RLE overruns glyph')
    im=Image.new('L',(width,height));im.putdata([v*36 for v in pixels])
    return im,2+(pos+1)//2

def encode(image):
    width,height=image.size
    if not(1<=width<=16 and 1<=height<=16):raise ValueError('Invalid native glyph size')
    pixels=[min(7,v//36) for v in image.getdata()];out=[];pos=0
    while pos<len(pixels):
        v=pixels[pos];count=1
        while pos+count<len(pixels) and pixels[pos+count]==v and count<16:count+=1
        if count>=2:out.extend((v,v,0 if count==16 else count))
        else:out.append(v)
        pos+=count
    if len(out)%2:out.append(0)
    result=bytes((0,((16-width)<<4)|(16-height)))+bytes((out[i]<<4)|out[i+1] for i in range(0,len(out),2))
    assert decode(result)[0].tobytes()==image.tobytes()
    return result

def get_glyph(code,rom,assets):
    source,base,table,count=TABLES[code>>8];index=code&255
    if index>=count:raise ValueError('Invalid glyph code')
    offset=struct.unpack_from('>H',rom,table+index*2)[0]
    data=rom if source=='rom' else assets[source]
    return decode(data,base+offset)[0]
