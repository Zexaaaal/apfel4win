from fontTools.ttLib import TTFont

def analyze_gsub(font_path):
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    rev_cmap = {v: k for k, v in cmap.items()}
    
    if 'GSUB' not in font:
        print("No GSUB found")
        return

    gsub = font['GSUB'].table
    total_ligatures = 0
    total_single = 0
    total_multiple = 0
    
    for lookup in gsub.LookupList.Lookup:
        actual_type = lookup.LookupType
        subtables = lookup.SubTable
        if actual_type == 7:
            actual_type = subtables[0].ExtensionLookupType
            subtables = [st.ExtSubTable for st in subtables]
            
        if actual_type == 1: # Single
            for st in subtables:
                total_single += len(st.mapping)
        elif actual_type == 2: # Multiple
            for st in subtables:
                total_multiple += len(st.mapping)
        elif actual_type == 4: # Ligature
            for st in subtables:
                if hasattr(st, 'LigatureSet'):
                    for first, lset in st.LigatureSet.items():
                        total_ligatures += len(lset.Ligature)
                        
    print(f"Single Substitutions: {total_single}")
    print(f"Multiple Substitutions: {total_multiple}")
    print(f"Ligature Substitutions: {total_ligatures}")
    
    # Check for skin tones specifically
    skins = {0x1F3FB, 0x1F3FC, 0x1F3FD, 0x1F3FE, 0x1F3FF}
    skin_gnames = {font.getGlyphName(cmap[s]) if isinstance(cmap[s], int) else cmap[s] for s in skins if s in cmap}
    
    skin_ligs = 0
    for lookup in gsub.LookupList.Lookup:
        actual_type = lookup.LookupType
        subtables = lookup.SubTable
        if actual_type == 7:
            actual_type = subtables[0].ExtensionLookupType
            subtables = [st.ExtSubTable for st in subtables]
        if actual_type == 4:
            for st in subtables:
                if hasattr(st, 'LigatureSet'):
                    for first, lset in st.LigatureSet.items():
                        for lig in lset.Ligature:
                            if any(c in skin_gnames for c in lig.Component):
                                skin_ligs += 1
                                
    print(f"Ligatures involving skin tones: {skin_ligs}")

if __name__ == "__main__":
    import os
    path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf')
    analyze_gsub(path)
