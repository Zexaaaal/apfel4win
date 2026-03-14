import os
import sys
import subprocess
import shutil
import ctypes
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if is_admin():
        return True
    
    logging.info("Requesting administrative privileges...")
    
    script = os.path.abspath(sys.argv[0])
    params = f'"{script}"'
    if len(sys.argv) > 1:
        params += " " + " ".join(f'"{a}"' for a in sys.argv[1:])
        
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, os.getcwd(), 1)
    
    if ret <= 32:
        logging.error(f"Failed to elevate. ShellExecute error code: {ret}")
        return False
        
    return True

def replace_font(new_font_path):
    target_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'seguiemj.ttf')
    backup_path = target_path + ".bak"
    
    logging.info(f"Target font: {target_path}")
    
    try:
        # 1. Take ownership
        logging.info("Taking ownership of the system font...")
        subprocess.run(['takeown', '/f', target_path], check=True, capture_output=True)
        
        # 2. Grant full control to current user
        username = os.environ.get('USERNAME')
        logging.info(f"Granting full control to {username}...")
        subprocess.run(['icacls', target_path, '/grant', f'{username}:F'], check=True, capture_output=True)
        
        # 3. Backup original if not already backed up
        if not os.path.exists(backup_path):
            logging.info(f"Creating backup at {backup_path}...")
            shutil.copy2(target_path, backup_path)
            
        try:
            # 4. ADVANCED: Unregister Font Resource to release system locks
            logging.info("Unregistering font resource from GDI...")
            gdi32 = ctypes.windll.gdi32
            user32 = ctypes.windll.user32
            gdi32.RemoveFontResourceW(target_path)
            
            # Notify apps (helps release handles)
            HWND_BROADCAST = 0xFFFF
            WM_FONTCHANGE = 0x001D
            user32.SendMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)

            # 5. Stop font services
            logging.info("Stopping Windows Font Cache services...")
            subprocess.run(['net', 'stop', 'FontCache', '/y'], capture_output=True)
            subprocess.run(['net', 'stop', 'FontCache3.0.0.0', '/y'], capture_output=True)
            
            # 6. Force Replacement Strategy
            pending_font = target_path + ".pending"
            logging.info(f"Copying new font to {pending_font}...")
            shutil.copy2(new_font_path, pending_font)
            
            # Try to Rename/Swap
            temp_old = target_path + ".old"
            success = False
            
            for attempt in range(2):
                try:
                    if os.path.exists(temp_old):
                        os.remove(temp_old)
                    
                    logging.info(f"Attempting RENAME (Attempt {attempt+1})...")
                    os.rename(target_path, temp_old)
                    os.rename(pending_font, target_path)
                    logging.info("SUCCESS: Font replaced successfully.")
                    success = True
                    break
                except OSError as e:
                    if attempt == 0:
                        logging.warning("RENAME failed. Attempting to kill Explorer.exe to release locks...")
                        subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], capture_output=True)
                    else:
                        logging.error(f"All direct and forced attempts failed: {e}")

            if success:
                # Clean up .old if possible
                try: os.remove(temp_old)
                except: pass
                
                # Restart explorer
                logging.info("Restarting Explorer...")
                subprocess.run(['start', 'explorer.exe'], shell=True)
                return True
            else:
                # FINAL ATTEMPT: Schedule for Reboot using Windows API
                logging.info("ALL LIVE ATTEMPTS FAILED. Scheduling replacement for next reboot...")
                MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
                MOVEFILE_REPLACE_EXISTING = 0x1
                
                # We schedule the .pending file to replace the target
                res = ctypes.windll.kernel32.MoveFileExW(
                    pending_font, 
                    target_path, 
                    MOVEFILE_DELAY_UNTIL_REBOOT | MOVEFILE_REPLACE_EXISTING
                )
                
                if res:
                    logging.info("SUCCESS: Replacement scheduled. The font will be replaced AUTOMATICALLY on your next restart.")
                    logging.warning("Please RESTART your computer now to see the changes.")
                    return True
                else:
                    logging.error(f"MoveFileExW failed with error code: {ctypes.windll.kernel32.GetLastError()}")
                    logging.info("FALLBACK: The font remains locked. Please replace it manually in Safe Mode or via a bootable USB.")
                    return False
                
        finally:
            # Restart services
            logging.info("Restarting Font Cache services...")
            subprocess.run(['net', 'start', 'FontCache'], capture_output=True)
            
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit()
    
    if len(sys.argv) > 1:
        replace_font(sys.argv[1])
    else:
        logging.error("No source font provided.")
