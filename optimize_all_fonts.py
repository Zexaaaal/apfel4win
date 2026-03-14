from fontTools.ttLib import TTFont, TTCollection
import os
import glob

def optimize_sbix_table(font, sizes_to_keep):
    if 'sbix' not in font:
        return False
    
    sbix = font['sbix']
    new_strikes = {}
    for ppem, strike in sbix.strikes.items():
        if ppem in sizes_to_keep:
            new_strikes[ppem] = strike
    
    if len(new_strikes) == len(sbix.strikes):
        return False
        
    sbix.strikes = new_strikes
    return True

def optimize_file(path, sizes_to_keep):
    print(f"Traitement de {path}...")
    try:
        temp_path = path + ".tmp"
        ext = os.path.splitext(path)[1].lower()
        
        changed = False
        if ext == '.ttc':
            collection = TTCollection(path)
            for font in collection:
                if optimize_sbix_table(font, sizes_to_keep):
                    changed = True
            if changed:
                collection.save(temp_path)
        else:
            font = TTFont(path)
            if optimize_sbix_table(font, sizes_to_keep):
                changed = True
                font.save(temp_path)
            font.close()

        if changed:
            old_size = os.path.getsize(path) / 1024 / 1024
            new_size = os.path.getsize(temp_path) / 1024 / 1024
            print(f"  Taille : {old_size:.2f} MB -> {new_size:.2f} MB")
            os.replace(temp_path, path)
        else:
            print(f"  Aucun changement nécessaire pour {path}.")
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"  Erreur sur {path}: {e}")

if __name__ == "__main__":
    essential_sizes = [20, 32, 64, 160]
    files = glob.glob("*.ttf") + glob.glob("*.ttc")
    for file in files:
        if os.path.getsize(file) > 10 * 1024 * 1024: # > 10 Mo
            optimize_file(file, essential_sizes)
