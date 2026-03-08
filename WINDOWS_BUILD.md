# Building for Windows

To create a Windows executable, you need to build on a Windows machine.

## Prerequisites (Windows)

### 1. Install Python
- Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation

### 2. Install System Dependencies

**Option A: Using Chocolatey (Recommended)**
```powershell
# Install Chocolatey first: https://chocolatey.org/install
choco install ffmpeg pngquant
```

**Option B: Manual Installation**
- **FFmpeg**: Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  - Add to PATH or place in `C:\Windows\System32`
- **pngquant**: Download from [pngquant.org](https://pngquant.org/)
  - Add to PATH

## Build Steps

### 1. Transfer Project to Windows

Zip your project (excluding build artifacts):
```bash
# On Mac
cd /Users/lloydturner/Documents/Refiner
zip -r Refiner-source.zip . -x "dist/*" -x "build/*" -x "venv/*" -x "__pycache__/*" -x "*.log"
```

Transfer `Refiner-source.zip` to your Windows machine and extract it.

### 2. Set Up Python Environment (Windows)

```powershell
cd Refiner
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 3. Build

```powershell
python build.py
```

## Output

- **File:** `dist\Refiner.exe`
- **Size:** ~150-200 MB
- **Type:** Standalone Windows executable

## Distribution

```powershell
# Zip the executable
cd dist
Compress-Archive -Path Refiner.exe -DestinationPath Refiner-Windows.zip
```

Share `Refiner-Windows.zip` with Windows users. They:
1. Download and extract
2. Double-click `Refiner.exe` to run
3. No installation required!

## Troubleshooting

### "ffmpeg not found" during build
- Verify: `ffmpeg -version` in Command Prompt
- If not found, reinstall and ensure it's in PATH

### "pngquant not found" during build
- Verify: `pngquant --version` in Command Prompt
- If not found, reinstall and ensure it's in PATH

### Windows Defender blocks the app
- This is common with PyInstaller executables (false positive)
- Add an exception or code-sign the executable

### Build fails with import errors
```powershell
pip install -r requirements-dev.txt --force-reinstall
```

## Alternative: Use GitHub Actions (Recommended)

The repo includes a GitHub Actions workflow (`.github/workflows/release.yml`) that
automatically builds both macOS and Windows binaries whenever you push a version tag.
No Windows machine needed — just tag a release and download the artifacts.

See the workflow file for details.

## Comparing Builds

| Feature | macOS | Windows |
|---------|-------|---------|
| Build command | `python3 build.py` | `python build.py` |
| Output | `Refiner.app` | `Refiner.exe` |
| Size | ~220-250 MB | ~150-200 MB |
| Distribution | Zip `.app` folder | Zip `.exe` file |

Both builds are standalone and don't require Python on the user's machine!
