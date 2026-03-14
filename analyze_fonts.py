from fontTools.ttLib import TTFont, TTCollection
import os


def analyze_font(path):
    print(f'\n--- Analyzing: {path} ---')
    if not os.path.exists(path):
        print('File does not exist.')
        return
    try:
        if path.lower().endswith('.ttc'):
            collection = TTCollection(path)
            print(f'Detected TrueType Collection with {len(collection)} fonts.'
                )
            for i, font in enumerate(collection):
                print(f'\n[Font {i}]')
                show_tables(font)
        else:
            font = TTFont(path)
            show_tables(font)
            font.close()
    except Exception as e:
        print(f'Error analyzing font: {e}')


def show_tables(font):
    print(f'Tables found: {list(font.keys())}')
    if 'sbix' in font:
        print("Detected 'sbix' table (Apple bitmap format).")
        sbix = font['sbix']
        strikes = sbix.strikes.keys()
        print(f'sbix strikes (resolutions): {list(strikes)}')
    if 'COLR' in font:
        print("Detected 'COLR' table (Windows vector format).")
    if 'CBDT' in font:
        print("Detected 'CBDT/CBLC' tables (Google/Windows bitmap format).")
    if 'SVG ' in font:
        print("Detected 'SVG ' table (Adobe/Mozilla vector format).")


if __name__ == '__main__':
    analyze_font('AppleColorEmoji-HD.ttc')
    analyze_font('seguiemj.ttf')