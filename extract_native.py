from fontTools.ttLib import TTFont
import os
segoe_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf.bak')
if not os.path.exists(segoe_path):
    print('BACKUP NOT FOUND')
    exit(1)
f = TTFont(segoe_path)
strike32 = f['sbix'].strikes[32]
gname = f.getBestCmap().get(128512)
if gname in strike32.glyphs:
    glyph = strike32.glyphs[gname]
    with open('segoe_32px_native.png', 'wb') as f_out:
        f_out.write(glyph.imageData)
    print(f'Extracted {gname} from 32px strike. See segoe_32px_native.png')
    from PIL import Image
    img = Image.open('segoe_32px_native.png')
    print(f'Native dimensions: {img.size}')
else:
    print(f'Glyph {gname} not found in 32px strike')