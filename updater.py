import os
import sys
import time
import shutil
import zipfile
import urllib.request
import subprocess
import json

VERSION_JSON_URL = "https://horizon-online.api-rapnss.workers.dev/versions.json"
OMNIAGENT_DATA_DIR = os.path.join(os.environ.get('USERPROFILE', ''), "AppData", "Local", "Omniagent")
BACKUP_DIR = os.path.join(os.environ.get('TEMP', ''), "Omniagent_Backup")

# Global log file path
LOG_FILE = None

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] [Updater] {msg}"
    print(full_msg)
    if LOG_FILE:
        try:
            with open(LOG_FILE, "a") as f:
                f.write(full_msg + "\n")
        except:
            pass

def backup_data():
    if os.path.exists(OMNIAGENT_DATA_DIR):
        log(f"Backing up memory from {OMNIAGENT_DATA_DIR} to {BACKUP_DIR}...")
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)
        shutil.copytree(OMNIAGENT_DATA_DIR, BACKUP_DIR)
        log("Backup complete.")
    else:
        log("No existing memory to backup.")

def restore_data():
    if os.path.exists(BACKUP_DIR):
        log(f"Restoring memory from {BACKUP_DIR} to {OMNIAGENT_DATA_DIR}...")
        if os.path.exists(OMNIAGENT_DATA_DIR):
            shutil.rmtree(OMNIAGENT_DATA_DIR)
        shutil.copytree(BACKUP_DIR, OMNIAGENT_DATA_DIR)
        shutil.rmtree(BACKUP_DIR)
        log("Restore complete.")
    else:
        log("No backup found to restore.")

def process_local_update(zip_path, target_dir):
    files_moved = 0
    temp_dir = os.path.join(os.environ.get('TEMP', ''), f"horizon_extract_{int(time.time())}")
    extract_dir = os.path.join(temp_dir, "extracted")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    log(f"Extracting {zip_path} into temporary directory...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Look for navigator.txt
    nav_file = os.path.join(extract_dir, "navigator.txt")
    
    # If not found at root, check if it's inside a single top-level folder
    if not os.path.exists(nav_file):
        try:
            possible_folders = [f for f in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, f))]
            if len(possible_folders) == 1:
                alt_nav = os.path.join(extract_dir, possible_folders[0], "navigator.txt")
                if os.path.exists(alt_nav):
                    nav_file = alt_nav
                    # Update extract_dir to the nested folder for easier relative pathing
                    extract_dir = os.path.join(extract_dir, possible_folders[0])
                    log(f"Redirecting base extraction dir to: {possible_folders[0]}")
        except: pass

    if os.path.exists(nav_file):
        log("Found navigator.txt, performing instruction-based update...")
        
        # Try different encodings to handle BOMs (Windows Notepad often adds them)
        lines = []
        for enc in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
            try:
                with open(nav_file, 'r', encoding=enc) as f:
                    lines = f.readlines()
                log(f"Successfully read navigator.txt with {enc} encoding.")
                break
            except:
                continue

        if not lines:
            log("Error: Could not read navigator.txt with any supported encoding.")
            return files_moved

        log(f"Read {len(lines)} lines from navigator.txt")
        for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Support -> or =>
                delimiter = '->' if '->' in line else '=>' if '=>' in line else None
                
                if not delimiter:
                    log(f"Skipping invalid line: '{line}' (no -> or =>)")
                    continue
                
                src_rel, dest_rel = [x.strip() for x in line.split(delimiter)]
                
                # Sourcing: Now that extract_dir might be redirected, simple join is best
                src_path = os.path.join(extract_dir, src_rel)
                dest_path = os.path.join(target_dir, dest_rel)
                
                if os.path.exists(src_path):
                    log(f"Updating: {src_rel} -> {dest_rel}")
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    if os.path.isdir(src_path):
                        if os.path.exists(dest_path):
                            shutil.rmtree(dest_path)
                        shutil.copytree(src_path, dest_path)
                    else:
                        shutil.copy2(src_path, dest_path)
                    files_moved += 1
                else:
                    log(f"Warning: Source file/folder '{src_rel}' not found in zip.")
                    # Show listing of current extract_dir for debugging
                    try:
                        log(f"Current Source Dir Listing: {os.listdir(extract_dir)}")
                    except: pass
    else:
        log("No navigator.txt found. Performing full merge...")
        for root, dirs, files in os.walk(extract_dir):
            rel_path = os.path.relpath(root, extract_dir)
            dest_root = os.path.join(target_dir, rel_path)
            os.makedirs(dest_root, exist_ok=True)
            for file in files:
                shutil.copy2(os.path.join(root, file), os.path.join(dest_root, file))

    log("Cleaning up temporary extraction files...")
    shutil.rmtree(temp_dir)
    # Also remove the source zip
    try:
        os.remove(zip_path)
    except:
        pass
    log("Processing complete.")
    return files_moved

def main():
    global LOG_FILE
    if len(sys.argv) < 3:
        log("Usage: updater.py <local_zip_path> <install_dir> [new_version]")
        sys.exit(1)

    local_zip_path = sys.argv[1]
    install_dir = sys.argv[2]
    new_version = sys.argv[3] if len(sys.argv) > 3 else None
    
    LOG_FILE = os.path.join(install_dir, "updater_log.txt")
    with open(LOG_FILE, "w") as f:
        f.write(f"--- Update Loop Start: {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    log(f"Background update started for: {local_zip_path}")
    log(f"Target directory: {install_dir}")

    try:
        # Backup user data
        backup_data()

        # Process the local update (Extract & Move based on navigator.txt)
        moved_count = process_local_update(local_zip_path, install_dir)

        # Update version.json if version provided and steps succeeded
        if new_version and moved_count > 0:
            log(f"Updating version.json to v{new_version}")
            version_file = os.path.join(install_dir, "version.json")
            try:
                with open(version_file, 'w') as f:
                    json.dump({"version": new_version}, f)
            except Exception as ve:
                log(f"Error updating version.json: {ve}")
        elif new_version:
            log("No files were moved, skipping version.json update.")

        # Restore user data
        restore_data()

        log("Update finished successfully. The user can now restart the application.")

    except Exception as e:
        log(f"CRITICAL ERROR during update: {e}")
        import traceback
        with open(os.path.join(install_dir, "updater_log.txt"), "a") as f:
            traceback.print_exc(file=f)
        restore_data()

if __name__ == "__main__":
    main()
