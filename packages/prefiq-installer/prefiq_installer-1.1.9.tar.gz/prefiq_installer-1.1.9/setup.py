import os
from setuptools import setup, find_packages
from pathlib import Path

# Read version from version.py
version_ns = {}
with open(os.path.join("core", "version.py")) as f:
    exec(f.read(), version_ns)
__version__ = version_ns.get("__version__", "0.0.1")

# Read long description from README.md
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="prefiq-installer",
    version=__version__,
    description="Installer for the prefiq CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/PREFIQ/prefiq-py-cli",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "prefiq=core.main:main"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.12",
)
