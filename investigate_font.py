from fontTools.ttLib import TTFont
import os

segoe_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf')
if not os.path.exists(segoe_path): segoe_path += ".bak"
apple_path = "AppleColorEmoji-160px.ttc"

segoe = TTFont(segoe_path)
apple_coll = TTFont(apple_path, fontNumber=0)

print(f"Segoe Tables: {sorted(segoe.keys())}")
print(f"Apple Tables: {sorted(apple_coll.keys())}")

def check_sbix(font, label, glyph_name):
    if 'sbix' in font:
        print(f"\n[{label}] sbix info for {glyph_name}:")
        for res, strike in sorted(font['sbix'].strikes.items()):
            if glyph_name in strike.glyphs:
                g = strike.glyphs[glyph_name]
                print(f"  Strike {res}px: ppem={strike.ppem}, offset=({g.originOffsetX}, {g.originOffsetY})")
            else:
                print(f"  Strike {res}px: GLYPH NOT FOUND")

# Glyph name for U+1F600 (Grinning Face)
g_segoe = segoe.getBestCmap().get(0x1F600)
g_apple = apple_coll.getBestCmap().get(0x1F600)

check_sbix(segoe, "Segoe", g_segoe)
check_sbix(apple_coll, "Apple", g_apple)

if 'GSUB' in apple_coll:
    print("\nApple GSUB found. Type:", apple_coll['GSUB'].table.Version)
else:
    print("\nApple GSUB NOT FOUND")

# Check for CBDT (Legacy Windows Color)
if 'CBDT' in segoe: print("Segoe uses CBDT/CBLC")
if 'sbix' in segoe: print("Segoe uses sbix")
