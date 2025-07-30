import argparse
import os
import shutil
import sys
import requests
import tempfile
import zipfile
import subprocess

INSTALL_DIR = os.path.join(sys.exec_prefix, "Scripts") if os.name == "nt" else os.path.join(sys.exec_prefix, "bin")
PREFIQ_NAME = "prefiq.exe" if os.name == "nt" else "prefiq"
PREFIQ_PATH = os.path.join(INSTALL_DIR, PREFIQ_NAME)
GIT_ZIP_URL = "https://github.com/PREFIQ/prefiq-py-cli/archive/refs/heads/main.zip"

def download_and_extract():
    print("Downloading prefiq.zip from GitHub...")
    response = requests.get(GIT_ZIP_URL)
    if response.status_code == 200:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "prefiq.zip")
            with open(zip_path, "wb") as f:
                f.write(response.content)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

                # Find the file inside .bin/ directory in extracted archive
                found = False
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        if file.lower() == PREFIQ_NAME:
                            if os.path.basename(os.path.dirname(file)).lower() == ".bin" or ".bin" in root:
                                src_path = os.path.join(root, file)
                                shutil.copy(src_path, PREFIQ_PATH)
                                print(f"Installed to {PREFIQ_PATH}")
                                found = True
                                break
                    if found:
                        break

                if not found:
                    print(f"{PREFIQ_NAME} not found in .bin folder of the zip.")
    else:
        print("Failed to download prefiq.zip")

def remove_exe():
    if os.path.exists(PREFIQ_PATH):
        os.remove(PREFIQ_PATH)
        print("prefiq removed.")
    else:
        print("prefiq not found.")

def get_version():
    if os.path.exists(PREFIQ_PATH):
        subprocess.run([PREFIQ_PATH, "--version"])
    else:
        print("prefiq not installed.")

def show_help():
    print("Usage:")
    print("  prefiq --version      Show version")
    print("  prefiq --help         Show help")
    print("  prefiq --update       Update prefiq")
    print("  prefiq --remove       Remove prefiq")

def check_and_add_path():
    path_env = os.environ.get("PATH", "")
    if INSTALL_DIR not in path_env:
        print(f"WARNING: {INSTALL_DIR} is not in your PATH.")
        if os.name == "nt":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
                    current_path = winreg.QueryValueEx(key, "Path")[0]
                    if INSTALL_DIR not in current_path:
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, f"{current_path};{INSTALL_DIR}")
                        print(f"Added {INSTALL_DIR} to user PATH. You may need to restart your terminal.")
            except Exception as e:
                print(f"Failed to update PATH: {e}")
        else:
            print(f"Please add {INSTALL_DIR} to your PATH manually.")

def main():
    parser = argparse.ArgumentParser(description="prefiq installer")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--update", action="store_true", help="Update prefiq")
    parser.add_argument("--remove", action="store_true", help="Remove prefiq")

    args, unknown = parser.parse_known_args()

    if "--help" in unknown:
        show_help()
    elif args.version:
        get_version()
    elif args.update:
        remove_exe()
        download_and_extract()
        check_and_add_path()
    elif args.remove:
        remove_exe()
    else:
        remove_exe()
        download_and_extract()
        check_and_add_path()

if __name__ == "__main__":
    main()
