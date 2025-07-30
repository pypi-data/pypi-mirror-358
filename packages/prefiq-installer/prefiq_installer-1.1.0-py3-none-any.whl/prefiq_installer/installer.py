import sys
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen
import tempfile
import zipfile
import os

GITHUB_ZIP_URL = "https://github.com/PREFIQ/prefiq-py-cli/archive/refs/heads/main.zip"
INSTALL_DIR = Path.home() / ".prefiq"

REQUIRED_FOLDERS = [
    "prefiq/templates",
    "prefiq/templates/prefentity",
    "prefiq/templates/app_full",
]

def check_python_version():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)

def download_zip_and_extract():
    print("Downloading Prefiq CLI package...")

    # Clean existing ZIP if it exists
    tmp_file_path = Path(tempfile.gettempdir()) / "prefiq_cli.zip"
    if tmp_file_path.exists():
        tmp_file_path.unlink()

    with urlopen(GITHUB_ZIP_URL) as resp, open(tmp_file_path, 'wb') as tmp_file:
        tmp_file.write(resp.read())

    print("Extracting package...")
    with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
        zip_ref.extractall(INSTALL_DIR)

    tmp_file_path.unlink()

def verify_required_folders(base_dir: Path):
    for rel_path in REQUIRED_FOLDERS:
        full_path = base_dir / rel_path
        if not full_path.exists():
            print(f"Error: Missing required folder: {full_path}")
            sys.exit(1)

def install_package():
    extracted_root = next(INSTALL_DIR.glob("prefiq-*"), None)
    if not extracted_root:
        print("Error: Extracted source folder not found.")
        sys.exit(1)

    verify_required_folders(extracted_root)

    print("Installing latest versions of prefiq-installer and prefiq...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "prefiq-installer", "prefiq"])

    print("Installing local prefiq CLI in editable mode...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(extracted_root)])

def main():
    check_python_version()

    if INSTALL_DIR.exists():
        print("Removing previous installation...")
        shutil.rmtree(INSTALL_DIR)

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        download_zip_and_extract()
        install_package()
        print("Prefiq CLI installed successfully.")
        print("You can now run: prefiq install <project-name>")
    except Exception as e:
        print(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
