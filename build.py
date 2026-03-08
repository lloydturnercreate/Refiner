"""
Build script for packaging Refiner as a standalone executable.

Usage:
    macOS/Linux:  python3 build.py
    Windows:      python build.py

Outputs:
    macOS  → dist/Refiner.app  (~220-250 MB)
    Windows → dist/Refiner.exe (~150-200 MB)
"""

import os
import sys
import platform
import subprocess
import shutil


APP_NAME = "Refiner"
ENTRY_POINT = "main.py"
ICON_DIR = "assets"


def clean():
    """Remove previous build artifacts."""
    for folder in ("build", "dist", "__pycache__"):
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}/")
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"Cleaned {spec_file}")


def find_icon():
    """Return platform-appropriate icon path if one exists, else None."""
    system = platform.system()
    candidates = {
        "Darwin": [
            os.path.join(ICON_DIR, "icon.icns"),
            os.path.join(ICON_DIR, "icon.png"),
        ],
        "Windows": [
            os.path.join(ICON_DIR, "icon.ico"),
            os.path.join(ICON_DIR, "icon.png"),
        ],
        "Linux": [
            os.path.join(ICON_DIR, "icon.png"),
        ],
    }
    for path in candidates.get(system, []):
        if os.path.exists(path):
            return path
    return None


def build():
    system = platform.system()
    print(f"Building for {system}...")

    args = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--clean",
        "--noconfirm",
        f"--add-data=assets{os.pathsep}assets",
        ENTRY_POINT,
    ]

    if system == "Darwin":
        args.append("--windowed")
    else:
        args.append("--onefile")

    icon = find_icon()
    if icon:
        args += ["--icon", icon]
        print(f"Using icon: {icon}")
    else:
        print("No icon found in assets/ — building without one.")

    # Hidden imports that PyInstaller may miss
    hidden = [
        "customtkinter",
        "PIL._tkinter_finder",
        "cairosvg",
        "cairocffi",
        "ffmpeg",
        "imageio_ffmpeg",
    ]
    for h in hidden:
        args += ["--hidden-import", h]

    # Collect imageio_ffmpeg in full so its bundled ffmpeg binary is included
    args += ["--collect-all", "imageio_ffmpeg"]

    print("Running PyInstaller…")
    result = subprocess.run(args, check=False)

    if result.returncode != 0:
        print("\nBuild FAILED. Check output above for details.")
        sys.exit(1)

    # Report output location
    if system == "Darwin":
        output = os.path.join("dist", f"{APP_NAME}.app")
    elif system == "Windows":
        output = os.path.join("dist", f"{APP_NAME}.exe")
    else:
        output = os.path.join("dist", APP_NAME)

    if os.path.exists(output):
        size_mb = _dir_size_mb(output) if os.path.isdir(output) else os.path.getsize(output) / 1_000_000
        print(f"\nBuild succeeded!")
        print(f"Output: {output}  ({size_mb:.0f} MB)")
    else:
        print(f"\nBuild finished but output not found at expected path: {output}")


def _dir_size_mb(path: str) -> float:
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total / 1_000_000


if __name__ == "__main__":
    clean()
    build()
