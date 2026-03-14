import sys
from fontTools.ttLib import TTFont
import os
if len(sys.argv) > 1:
    segoe_path = sys.argv[1]
else:
    segoe_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf')
    if not os.path.exists(segoe_path):
        segoe_path += '.bak'
if not os.path.exists(segoe_path):
    print(f'File not found: {segoe_path}')
    sys.exit(1)
f = TTFont(segoe_path)
cmap = f.getBestCmap()
rev_cmap = {v: k for k, v in cmap.items()}
print(f'Analyzing GSUB for {segoe_path}...')
if 'GSUB' in f:
    gsub = f['GSUB'].table
    count = 0
    for lookup_idx, lookup in enumerate(gsub.LookupList.Lookup):
        actual_type = lookup.LookupType
        for subtable in lookup.SubTable:
            st = subtable
            if actual_type == 7:
                st = st.ExtSubTable
            if (lookup.LookupType == 4 or actual_type == 7 and subtable.
                ExtensionLookupType == 4):
                if hasattr(st, 'LigatureSet'):
                    for input_glyph, ligatures in st.LigatureSet.items():
                        for lig in ligatures.Ligature:
                            comp_glyphs = [input_glyph] + lig.Component
                            comp_codes = []
                            for cg in comp_glyphs:
                                if cg in rev_cmap:
                                    comp_codes.append(f'{rev_cmap[cg]:04X}')
                                else:
                                    comp_codes.append(f'({cg})')
                            lig_glyph = lig.LigGlyph
                            print(
                                f"  LIG: {'_'.join(comp_codes)} -> {lig_glyph}"
                                )
                            count += 1
                            if count >= 50:
                                break
                        if count >= 50:
                            break
                    if count >= 50:
                        break
        if count >= 50:
            break
else:
    print('No GSUB table found.')