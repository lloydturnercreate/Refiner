# Refiner Dependencies

## System Dependencies (Required)

```bash
# Video processing
brew install ffmpeg

# Advanced PNG compression (optional but recommended)
brew install pngquant
```

## Python Dependencies (Required)

```bash
pip install -r requirements.txt
```

Or individually:

```bash
pip3 install customtkinter    # Modern GUI framework
pip3 install pillow           # Image processing (with AVIF support)
pip3 install ffmpeg-python    # Python wrapper for FFmpeg
pip3 install cairosvg         # SVG to raster conversion
```

## Dev / Build Dependencies

```bash
pip install -r requirements-dev.txt
```

Includes everything above plus:
- `pyinstaller` — package as standalone app/exe
- `pytest` — run the test suite

## Verification

### Test System Dependencies
```bash
ffmpeg -version
pngquant --version
```

### Test Python Dependencies
```bash
python3 -c "
import customtkinter
from PIL import Image, features
import ffmpeg
import cairosvg
print('All dependencies working!')
print(f'CustomTkinter: {customtkinter.__version__}')
print(f'Pillow: {Image.__version__}')
print(f'AVIF support: {features.check(\"avif\")}')
print('ffmpeg-python: Available')
print('CairoSVG: Available')
"
```

### Run Application
```bash
cd /path/to/Refiner
python3 main.py
```

## Supported Formats

### Images
- PNG, JPG, WebP, AVIF, SVG, BMP

### Videos
- MP4, WebM, MOV, GIF

## Notes

- CairoSVG is required for SVG conversion support
- pngquant is optional but provides significantly better PNG compression than Pillow alone
- FFmpeg must be available on the system PATH for all video operations
