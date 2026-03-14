import os
import sys
import io
import logging
from fontTools.ttLib import TTFont, TTCollection, newTable
from fontTools.ttLib.tables._s_b_i_x import Strike
from fontTools.ttLib.tables.sbixGlyph import Glyph as sbixGlyph
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def scale_glyph(glyph, factor):
    """Deep scale a glyf.Glyph coordinates."""
    if hasattr(glyph, 'coordinates') and glyph.coordinates is not None:
        try:
            glyph.coordinates.scale((factor, factor))
        except:
            new_coords = []
            for x, y in glyph.coordinates:
                new_coords.append((x * factor, y * factor))
            glyph.coordinates = new_coords
    if hasattr(glyph, 'components') and glyph.components is not None:
        for component in glyph.components:
            try:
                component.x = int(component.x * factor)
                component.y = int(component.y * factor)
            except: pass
    for attr in ['xMin', 'yMin', 'xMax', 'yMax']:
        if hasattr(glyph, attr) and getattr(glyph, attr) is not None:
            setattr(glyph, attr, int(getattr(glyph, attr) * factor))

class EmojiConverter:
    def __init__(self, apple_font_path, segoe_font_path):
        self.apple_font_path = apple_font_path
        self.segoe_font_path = segoe_font_path

    def get_segui_mappings(self, font):
        """Map Segoe Glyph IDs to Unicode Sequences (including Ligatures)."""
        cmap = font.getBestCmap()
        rev_cmap = {v: k for k, v in cmap.items()}
        mappings = {}
        
        # Simple Unicodes
        for code, g in cmap.items():
            mappings[g] = (code,)
            
        # Ligatures via GSUB
        if 'GSUB' in font:
            gsub = font['GSUB'].table
            for lookup in gsub.LookupList.Lookup:
                actual_type = lookup.LookupType
                subtables = lookup.SubTable
                if actual_type == 7: # Extension
                    actual_type = subtables[0].ExtensionLookupType
                    subtables = [st.ExtSubTable for st in subtables]
                    
                if actual_type == 4: # Ligature Substitution
                    for st in subtables:
                        if hasattr(st, 'LigatureSet'):
                            for first_glyph, ligatures in st.LigatureSet.items():
                                for lig in ligatures.Ligature:
                                    comp_glyphs = [first_glyph] + lig.Component
                                    comp_codes = []
                                    failed = False
                                    for cg in comp_glyphs:
                                        if cg in rev_cmap:
                                            comp_codes.append(rev_cmap[cg])
                                        else: failed = True; break
                                    if not failed:
                                        mappings[lig.LigGlyph] = tuple(comp_codes)
        return mappings

    def get_apple_sequence_map(self, font):
        """Build a CLEAN map of SequenceTuple -> Apple Glyph Name."""
        glyph_order = font.getGlyphOrder()
        apple_map = {}
        
        # Build clean sequences (strip FE0F and ZWJ from internal patterns)
        def clean_seq(seq):
            return tuple(x for x in seq if x not in (0xFE0F, 0x200D))

        # CMAP first
        cmap = font.getBestCmap()
        for code, g in cmap.items():
            s = (code,)
            apple_map[clean_seq(s)] = g
            
        # Glyph Names
        for gname in glyph_order:
            clean_name = gname.split('.')[0]
            parts = clean_name.split('_')
            sequence = []
            valid = True
            for p in parts:
                p_lower = p.lower()
                if p_lower.startswith('u') and all(c in '0123456789abcdef' for c in p_lower[1:]):
                    sequence.append(int(p_lower[1:], 16))
                elif p_lower.startswith('uni') and all(c in '0123456789abcdef' for c in p_lower[3:]):
                    sequence.append(int(p_lower[3:], 16))
                else:
                    valid = False
                    break
            if valid and sequence:
                c_seq = clean_seq(sequence)
                if c_seq not in apple_map or '.' not in gname:
                    apple_map[c_seq] = gname
                    
        return apple_map

    def convert(self, output_path):
        logging.info("Opening fonts...")
        apple_coll = TTCollection(self.apple_font_path)
        apple_font = apple_coll[0]
        segoe_font = TTFont(self.segoe_font_path)
            
        logging.info("SCALING OUTLINES (2048 -> 800 UPEM)...")
        old_upem = segoe_font['head'].unitsPerEm
        scale_factor = 800 / old_upem
        segoe_font['head'].unitsPerEm = 800
        
        glyf = segoe_font['glyf']
        for gname in segoe_font.getGlyphOrder():
             scale_glyph(glyf[gname], scale_factor)
             
        logging.info("Applying MAXIMUM HEIGHT METRICS (800/-50)...")
        segoe_font['hhea'].ascent = 800
        segoe_font['hhea'].descent = -50
        if 'OS/2' in segoe_font:
            os2 = segoe_font['OS/2']
            os2.version = 4
            os2.sTypoAscender = 800
            os2.sTypoDescender = -50
            os2.usWinAscent = 800
            os2.usWinDescent = 50
            os2.fsSelection = 64 | 128
            os2.sCapHeight = 800
            os2.sxHeight = 500

        logging.info("Analyzing Mappings...")
        segoe_map = self.get_segui_mappings(segoe_font)
        apple_seq_map = self.get_apple_sequence_map(apple_font)
        
        sbix = apple_font['sbix']
        best_res = 160 if 160 in sbix.strikes else sorted(sbix.strikes.keys())[-1]
        apple_strike = sbix.strikes[best_res]
        
        logging.info("Building 10-strike sbix table...")
        target_res = [20, 24, 32, 40, 48, 64, 72, 96, 128, 160]
        new_sbix = newTable('sbix')
        new_sbix.version = 1
        new_sbix.strikes = {}
        for res in target_res:
            s = Strike(); s.ppem = res; s.resolution = 72; s.glyphs = {}
            new_sbix.strikes[res] = s
            
        count = 0
        hmtx = segoe_font['hmtx'].metrics
        fixed_metrics = {}
        for gname in segoe_font.getGlyphOrder():
             fixed_metrics[gname] = (int(hmtx[gname][0] * scale_factor), int(hmtx[gname][1] * scale_factor))

        apple_pil_cache = {}
        logging.info("Processing glyphs with Permissive Mapping...")
        for gname, sequence in segoe_map.items():
            # Clean segoe sequence (strip VS and ZWJ for matching)
            clean_segoe = tuple(x for x in sequence if x not in (0xFE0F, 0x200D))
            apple_gname = apple_seq_map.get(clean_segoe)

            if apple_gname and apple_gname in apple_strike.glyphs:
                glyph_data = apple_strike.glyphs[apple_gname]
                if not glyph_data.imageData: continue
                
                # FORCE 800 ADVANCE
                fixed_metrics[gname] = (800, 0)
                
                try:
                    if apple_gname not in apple_pil_cache:
                        img = Image.open(io.BytesIO(glyph_data.imageData)).convert("RGBA")
                        apple_pil_cache[apple_gname] = img
                    
                    base_img = apple_pil_cache[apple_gname]
                    count += 1
                    for res in target_res:
                        resized_img = base_img.resize((res, res), Image.LANCZOS)
                        buf = io.BytesIO(); resized_img.save(buf, format="PNG")
                        g = sbixGlyph(); g.glyphName = gname; g.graphicType = 'png '; g.imageData = buf.getvalue()
                        g.originOffsetX = 0; g.originOffsetY = 0
                        new_sbix.strikes[res].glyphs[gname] = g
                except: pass

        segoe_font['hmtx'].metrics = fixed_metrics
        for tag in ['COLR', 'CPAL', 'SVG ', 'sbix', 'DSIG']:
            if tag in segoe_font: del segoe_font[tag]
        segoe_font['sbix'] = new_sbix
        segoe_font['head'].flags |= (1 << 11)
        
        logging.info(f"Successfully mapped {count} glyphs. Saving...")
        segoe_font.save(output_path)
        logging.info(f"Done! {output_path}")

if __name__ == "__main__":
    converter = EmojiConverter("AppleColorEmoji-160px.ttc", "seguiemj.ttf")
    converter.convert("seguiemj_new.ttf")
