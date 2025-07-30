import sys
import shutil
import subprocess
import platform
from pathlib import Path
from urllib.request import urlopen
import tempfile
import zipfile
import os

GITHUB_ZIP_URL = "https://github.com/YOUR_USERNAME/prefiq/archive/refs/heads/main.zip"
INSTALL_DIR = Path.home() / ".prefiq"

def check_python_version():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python 3.8+ is required. Please upgrade your Python.")
        sys.exit(1)

def download_zip_and_extract():
    with urlopen(GITHUB_ZIP_URL) as resp:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(resp.read())
            tmp_file.close()

            with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                zip_ref.extractall(INSTALL_DIR)
            os.unlink(tmp_file.name)

def install_package():
    extracted_root = next(INSTALL_DIR.glob("prefiq-*"))
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(extracted_root)])

def main():
    check_python_version()

    if INSTALL_DIR.exists():
        print("🧹 Cleaning up previous install...")
        shutil.rmtree(INSTALL_DIR)

    print("📥 Downloading and installing Prefiq CLI...")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    download_zip_and_extract()
    install_package()
    print("✅ Prefiq CLI installed successfully!")
    print("👉 Try running: prefiq install sundar")

if __name__ == "__main__":
    main()
