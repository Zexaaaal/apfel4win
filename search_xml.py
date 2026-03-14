import re

with open("seguiemj_gsub.ttx", "r") as f:
    content = f.read()

# Look for Ninja (u1F977) in Ligature tags
pattern = re.compile(r'<LigatureSet glyph="u1F977">.*?</LigatureSet>', re.DOTALL)
match = pattern.search(content)
if match:
    print("Found LigatureSet for u1F977:")
    print(match.group(0))
else:
    # Maybe Ninja is a component?
    print("Ninja not a first glyph. Searching for Ninja as a component...")
    pattern2 = re.compile(r'<Ligature components=".*?u1F977.*?" glyph="(.*?)"/>')
    matches = pattern2.findall(content)
    for m in matches:
        print(f"Ninja is a component mapping to glyph: {m}")
