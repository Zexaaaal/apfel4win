from fontTools.ttLib import TTCollection
import os
apple_path = 'AppleColorEmoji-160px.ttc'
if os.path.exists(apple_path):
    coll = TTCollection(apple_path)
    print(f'Collection contains {len(coll)} fonts.')
    for i, f in enumerate(coll):
        name = f['name'].getDebugName(1)
        tables = sorted(f.keys())
        glyph_count = len(f.getGlyphOrder())
        print(f'\nIndex {i}: {name}')
        print(f'  Tables: {tables}')
        print(f'  Glyphs: {glyph_count}')
        if 'GSUB' in f:
            print(
                f"  GSUB present! Lookups: {len(f['GSUB'].table.LookupList.Lookup)}"
                )
        if 'sbix' in f:
            print(f"  sbix present! Strikes: {list(f['sbix'].strikes.keys())}")
else:
    print('Apple font not found.')