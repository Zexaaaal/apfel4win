from fontTools.ttLib import TTFont, TTCollection
import os


def get_unicode_mapping(font):
    cmap = font['cmap'].getBestCmap()
    return {v: k for k, v in cmap.items()}


def compare_fonts(apple_path, segoe_path):
    apple_coll = TTCollection(apple_path)
    apple_font = apple_coll[0]
    segoe_font = TTFont(segoe_path)
    apple_cmap = apple_font['cmap'].getBestCmap()
    segoe_cmap = segoe_font['cmap'].getBestCmap()
    apple_unicodes = set(apple_cmap.keys())
    segoe_unicodes = set(segoe_cmap.keys())
    common = apple_unicodes.intersection(segoe_unicodes)
    only_apple = apple_unicodes - segoe_unicodes
    only_segoe = segoe_unicodes - apple_unicodes
    print(f'Common Unicodes: {len(common)}')
    print(f'Unicodes only in Apple: {len(only_apple)}')
    print(f'Unicodes only in Segoe: {len(only_segoe)}')
    sbix = apple_font['sbix']
    strike_res = max(sbix.strikes.keys())
    strike = sbix.strikes[strike_res]
    glyphs_with_bitmaps = [g for g in strike.glyphs.keys() if strike.glyphs
        [g].imageData is not None]
    print(
        f'Apple Glyphs with Bitmaps in {strike_res}px strike: {len(glyphs_with_bitmaps)}'
        )


if __name__ == '__main__':
    compare_fonts('AppleColorEmoji-HD.ttc', 'seguiemj.ttf')