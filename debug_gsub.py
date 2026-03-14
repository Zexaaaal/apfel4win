from fontTools.ttLib import TTFont


def debug_gsub(font_path):
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    rev_cmap = {v: k for k, v in cmap.items()}
    skins = {127995, 127996, 127997, 127998, 127999}
    skin_gnames = {(font.getGlyphName(cmap[s]) if isinstance(cmap[s], int) else
        cmap[s]) for s in skins if s in cmap}
    print(f'Skin glyph names in Segoe: {skin_gnames}')
    if 'GSUB' not in font:
        print('No GSUB found')
        return
    gsub = font['GSUB'].table
    ligs_with_skins = 0
    sample_ligs = []
    for lookup in gsub.LookupList.Lookup:
        actual_type = lookup.LookupType
        subtables = lookup.SubTable
        if actual_type == 7:
            actual_type = subtables[0].ExtensionLookupType
            subtables = [st.ExtSubTable for st in subtables]
        if actual_type == 4:
            for st in subtables:
                if not hasattr(st, 'LigatureSet'):
                    continue
                for first, ligatures in st.LigatureSet.items():
                    first_code = rev_cmap.get(first)
                    for lig in ligatures.Ligature:
                        comp_codes = []
                        has_skin = False
                        for c in lig.Component:
                            if c in skin_gnames:
                                has_skin = True
                            ccode = rev_cmap.get(c)
                            if ccode:
                                comp_codes.append(f'u{ccode:04X}')
                            else:
                                comp_codes.append(c)
                        if has_skin:
                            ligs_with_skins += 1
                            if len(sample_ligs) < 20:
                                first_hex = (f'u{first_code:04X}' if
                                    first_code else first)
                                sample_ligs.append(
                                    f"{first_hex} + {' + '.join(comp_codes)} -> {lig.LigGlyph}"
                                    )
    print(f'Total skin tone ligatures: {ligs_with_skins}')
    print('Sample skin ligatures:')
    for sl in sample_ligs:
        print(f'  {sl}')


if __name__ == '__main__':
    debug_gsub('seguiemj.ttf')