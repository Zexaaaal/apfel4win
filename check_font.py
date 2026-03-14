from fontTools.ttLib import TTFont
import os

def check_generated_font(path):
    if not os.path.exists(path):
        print("File not found.")
        return
    
    font = TTFont(path)
    print(f"Checking: {path}")
    print(f"Tables: {list(font.keys())}")
    
    if 'sbix' in font:
        sbix = font['sbix']
        print(f"sbix version: {sbix.version}")
        for res, strike in sbix.strikes.items():
            mapped_count = len([g for g in strike.glyphs.values() if g.imageData])
            print(f"Strike {res}px: {mapped_count} glyphs with color data")
            
    if 'CPAL' in font:
        print(f"CPAL table found. Palettes: {len(font['CPAL'].palettes)}")
    else:
        print("CPAL table MISSING!")

    if 'OS/2' in font:
        print(f"OS/2 version: {font['OS/2'].version}, Vendor: {font['OS/2'].achVendID}")

    if 'COLR' in font:
        print(f"COLR table found (Unexpected if we want sbix to rule)")
    else:
        print("COLR table removed (Good for sbix precedence)")
            
    font.close()

if __name__ == "__main__":
    check_generated_font("seguiemj_new.ttf")
