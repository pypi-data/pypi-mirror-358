import sys
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
import tempfile
import zipfile
import os
import importlib.metadata
import json
from datetime import datetime

INSTALL_DIR = Path.home() / ".prefiq"
LOG_FILE = INSTALL_DIR / "installer.log"
REQUIRED_FOLDERS = [
    "prefiq/templates",
    "prefiq/templates/prefentity",
    "prefiq/templates/app_full",
]

GITHUB_API_RELEASE_URL = "https://api.github.com/repos/PREFIQ/prefiq-py-cli/releases/latest"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(msg)

def check_python_version():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 12):
        log(f"Python 3.12 or higher is required. Detected: {sys.version}")
        sys.exit(1)

def get_latest_release_zip_url():
    req = Request(GITHUB_API_RELEASE_URL, headers={"Accept": "application/vnd.github+json"})
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        zip_url = data.get("zipball_url")
        if not zip_url:
            raise Exception("Could not retrieve latest release ZIP URL.")
        return zip_url

def get_installed_version(package: str):
    try:
        version = importlib.metadata.version(package)
        location = importlib.metadata.distribution(package).locate_file('').resolve()
        return version, location
    except importlib.metadata.PackageNotFoundError:
        return None, None

def download_zip_and_extract(zip_url):
    log("Downloading Prefiq CLI source package...")
    tmp_file_path = Path(tempfile.gettempdir()) / "prefiq_cli.zip"
    if tmp_file_path.exists():
        tmp_file_path.unlink()

    with urlopen(zip_url) as resp, open(tmp_file_path, 'wb') as tmp_file:
        tmp_file.write(resp.read())

    log("Extracting package...")
    with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
        zip_ref.extractall(INSTALL_DIR)

    tmp_file_path.unlink()

def verify_required_folders(base_dir: Path):
    for rel_path in REQUIRED_FOLDERS:
        full_path = base_dir / rel_path
        if not full_path.exists():
            log(f"Missing required folder: {full_path}")
            sys.exit(1)

def install_package():
    extracted_root = next(INSTALL_DIR.glob("prefiq-*"), None)
    if not extracted_root:
        log("Error: Extracted source folder not found.")
        sys.exit(1)

    verify_required_folders(extracted_root)

    log("\nChecking existing package versions...")
    for pkg in ["prefiq-installer", "prefiq"]:
        prev_version, prev_path = get_installed_version(pkg)
        if prev_version:
            log(f"{pkg} previously installed: v{prev_version} at {prev_path}")
        else:
            log(f"{pkg} not previously installed")

    log("\nInstalling latest versions of prefiq-installer and prefiq...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "prefiq-installer", "prefiq"
    ])

    for pkg in ["prefiq-installer", "prefiq"]:
        new_version, new_path = get_installed_version(pkg)
        log(f"{pkg} now installed: v{new_version} at {new_path}")

    log("\nInstalling Prefiq CLI in editable mode...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", str(extracted_root)])

def uninstall_prefiq():
    log("Uninstalling Prefiq CLI and cleaning up...")
    for pkg in ["prefiq", "prefiq-installer"]:
        subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", pkg])
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
    log("Prefiq has been removed successfully.")

def main():
    check_python_version()

    if "--reset" in sys.argv:
        uninstall_prefiq()
        return

    if "--v" in sys.argv:
        version, path = get_installed_version("prefiq-installer")
        if version:
            print(f"Prefiq Installer version: {version} at {path}")
        else:
            print("Prefiq Installer is not currently installed.")
        return

    log("Starting Prefiq CLI installation...\n")

    if INSTALL_DIR.exists():
        log("Cleaning previous install...")
        shutil.rmtree(INSTALL_DIR)

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        zip_url = get_latest_release_zip_url()
        download_zip_and_extract(zip_url)
        install_package()
        log("\nPrefiq CLI installation completed successfully.")
        log("You can now run: prefiq install <project-name>")
    except Exception as e:
        log(f"\nInstallation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()