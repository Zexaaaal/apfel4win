import re
with open('seguiemj_gsub.ttx', 'r') as f:
    content = f.read()
pattern = re.compile('<LigatureSet glyph="u1F977">.*?</LigatureSet>', re.DOTALL
    )
match = pattern.search(content)
if match:
    print('Found LigatureSet for u1F977:')
    print(match.group(0))
else:
    print('Ninja not a first glyph. Searching for Ninja as a component...')
    pattern2 = re.compile('<Ligature components=".*?u1F977.*?" glyph="(.*?)"/>'
        )
    matches = pattern2.findall(content)
    for m in matches:
        print(f'Ninja is a component mapping to glyph: {m}')