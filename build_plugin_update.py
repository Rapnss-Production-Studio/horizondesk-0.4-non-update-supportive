import os
import zipfile
import shutil

TARGET_ZIP = "v0.3-plugin-update.zip"

def main():
    if os.path.exists(TARGET_ZIP):
        os.remove(TARGET_ZIP)

    print(f"Creating {TARGET_ZIP}...")

    # Files and directories to include
    # We must preserve the relative paths so updater.py overlays them correctly
    includes = [
        "main.py",
        "updater.py",
        "update_check.py",
        "core",
        "tools",
        "sample-gui/dist",
        "sample-gui/main_gui.py"
    ]

    with zipfile.ZipFile(TARGET_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in includes:
            if not os.path.exists(item):
                print(f"Warning: {item} does not exist. Skipping.")
                continue

            if os.path.isfile(item):
                print(f"Adding file: {item}")
                zipf.write(item, item)
            elif os.path.isdir(item):
                print(f"Adding directory: {item}")
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Optional: skip __pycache__ etc
                        if "__pycache__" in file_path or file_path.endswith(".pyc"):
                            continue
                        zipf.write(file_path, file_path)

    print(f"Successfully created {TARGET_ZIP}")

if __name__ == "__main__":
    main()
