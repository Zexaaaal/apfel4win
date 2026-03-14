from fontTools.ttLib import TTFont, TTCollection
import os
apple_path = 'AppleColorEmoji-160px.ttc'
segoe_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf.bak')
apple = TTCollection(apple_path)[0]
segoe = TTFont(segoe_path)


def get_apple_seq(font):
    order = font.getGlyphOrder()
    res = {}
    for gname in order:
        clean = gname.split('.')[0]
        parts = clean.split('_')
        seq = []
        try:
            for p in parts:
                if p.startswith('u'):
                    seq.append(int(p[1:], 16))
                elif p.startswith('uni'):
                    seq.append(int(p[3:], 16))
            if seq:
                res[tuple(seq)] = gname
        except:
            pass
    return res


apple_map = get_apple_seq(apple)
test_seqs = [(128104,), (128104, 127995), (128104, 127999), (129399,), (
    129399, 127995)]
print('--- Apple Mappings ---')
for s in test_seqs:
    print(f"Sequence {s}: {apple_map.get(s, 'NOT FOUND')}")
cmap = segoe.getBestCmap()
print("""
--- Segoe CMAP ---""")
for s in test_seqs:
    if len(s) == 1:
        print(f"Code {s[0]:04X}: {cmap.get(s[0], 'NOT FOUND')}")