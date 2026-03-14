import os
from fontTools.ttLib import TTFont
sys_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf')
pend_path = sys_path + '.pending'
print(f'Checking {sys_path}')
if os.path.exists(sys_path):
    print(f'System Font Size: {os.path.getsize(sys_path)}')
    try:
        f = TTFont(sys_path)
        print(f'System Font Tables: {sorted(f.keys())}')
        if 'sbix' in f:
            print(f"System Font Strikes: {sorted(f['sbix'].strikes.keys())}")
    except Exception as e:
        print(f'Error reading system font: {e}')
else:
    print('System Font MISSING!')
print(f'Checking {pend_path}')
if os.path.exists(pend_path):
    print(f'Pending Font Size: {os.path.getsize(pend_path)}')
else:
    print('Pending Font MISSING')
local_gen = 'seguiemj_new.ttf'
if os.path.exists(local_gen):
    print(f'Local Generated Size: {os.path.getsize(local_gen)}')
    f = TTFont(local_gen)
    print(f"Local Generated Strikes: {sorted(f['sbix'].strikes.keys())}")