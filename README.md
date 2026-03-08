# Refiner - Image & Video Converter & Compressor

An application for converting and compressing images and videos.

## Features

### Core Capabilities
- **Format Conversion**: Convert between multiple image and video formats
- **Smart Compression**: Compress files with adjustable quality levels (0-100 scale)
- **Real-time Predictions**: See estimated output file sizes before compressing
- **Dual-Mode Interface**: Separate tabs for conversion and compression workflows
- **Advanced PNG Compression**: Automatic fallback to pngquant for superior PNG compression
- **Professional Video Encoding**: FFmpeg-powered video processing with optimized settings

### Images
- PNG (with pngquant optimization)
- JPG/JPEG
- WebP
- AVIF
- BMP
- SVG (read-only, converts to raster formats)

### Videos
- MP4 (H.264)
- WebM (VP9)
- MOV (H.264)
- GIF (with palette optimization)

## Installation

### Prerequisites

1. **Python 3.9+** - Required for running the application
2. **FFmpeg** - Required for video processing
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **pngquant** (Optional) - Enhanced PNG compression
   ```bash
   # macOS
   brew install pngquant
   
   # Ubuntu/Debian
   sudo apt install pngquant
   
   # Windows
   # Download from https://pngquant.org/
   ```

### Python Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install customtkinter Pillow ffmpeg-python cairosvg
```

## Usage

### Starting the Application

```bash
python main.py
```

### Converting Files

1. Switch to the **Converter** tab
2. Click **Browse** next to Source to select your file
3. Choose the output format from the **Format** dropdown
4. Optionally change the output path via **Save As**
5. Click **Convert**

**Note**: SVG files can only be converted to raster formats (PNG, JPG, etc.), not from them.

### Compressing Files

1. Switch to the **Compressor** tab
2. Click **Browse** next to Source to select your file
3. Adjust the **Compression** slider (0 = minimal, 100 = maximum)
4. Preview the predicted file size in real-time
5. Click **Compress**

**Compression Scale**:
- **0-30**: Light compression, maintains high quality
- **30-70**: Balanced compression, good quality/size ratio
- **70-100**: Heavy compression, prioritizes file size

## Project Architecture

### Modular Structure

```
Refiner/
├── main.py                 # Application entry point
├── ui_components.py        # CustomTkinter UI implementation
├── converters.py           # Image & video conversion classes
├── compressors.py          # Image & video compression classes
├── constants.py            # Configuration constants & settings
├── utils.py                # Utility functions & helpers
├── logger.py               # Logging configuration
├── build.py                # PyInstaller packaging script
├── tests/                  # Test suite
├── logs/                   # Application logs (auto-generated)
└── assets/                 # UI assets (icons, logo)
```

### Design Principles

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Factory Pattern**: Automatic selection of appropriate converter/compressor
- **Configuration-Driven**: All settings centralized in `constants.py`
- **Error Resilience**: Comprehensive error handling with graceful fallbacks
- **Extensibility**: Easy to add new formats or compression strategies

## Technical Details

### Image Processing

- **Pillow** handles format conversion and basic compression
- **pngquant** provides advanced PNG compression (auto-fallback to Pillow if unavailable)
- **CairoSVG** enables SVG to raster conversion
- **Quality Mapping**: 0-100 slider maps to format-specific quality parameters

### Video Processing

- **FFmpeg** powers all video operations
- **Bitrate Calculation**: Dynamic bitrate targeting based on compression level
- **Codec Selection**:
  - MP4/MOV: H.264 (libx264) with CRF 18
  - WebM: VP9 (libvpx-vp9) with CRF 30
  - GIF: Palette-based encoding with adjustable color reduction

### Real-Time Prediction

The compressor provides instant file size predictions:
- **Images**: Encodes to in-memory buffer for accurate size estimation
- **Videos**: Calculates predicted bitrate based on compression level
- **Debounced Updates**: 500ms delay prevents excessive calculations

### Logging System

- **Dual Output**: Console (INFO+) and file (DEBUG+)
- **Daily Rotation**: New log file created each day
- **Platform-aware**: Logs stored in OS-appropriate locations
  - macOS: `~/Library/Logs/Refiner/logs/`
  - Windows: `%APPDATA%/Refiner/logs/`
  - Linux: `~/.local/state/Refiner/logs/`

## Development

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Building for Distribution

```bash
pip install -r requirements-dev.txt
python build.py
```

Outputs:
- macOS: `dist/Refiner.app`
- Windows: `dist/Refiner.exe`
- Linux: `dist/Refiner`

### Adding New Image Formats

1. Add extension to `IMAGE_EXTENSIONS` in `constants.py`
2. Update `format_map` in `ImageConverter._get_output_format()`
3. Test conversion and compression workflows

### Adding New Video Codecs

1. Add extension to `VIDEO_EXTENSIONS` in `constants.py`
2. Implement conversion method in `VideoConverter` class
3. Update `CompressorFactory` if needed for compression support
4. Add constants for codec-specific settings (CRF, preset, etc.)

### Customizing the UI

All UI constants are in `constants.py`:
- **Colors**: `BACKGROUND_PRIMARY`, `ACCENT_PRIMARY`, etc.
- **Typography**: `FONT_FAMILY`, `FONT_SIZE_*`
- **Spacing**: `SPACING_*`, `RADIUS_*`
- **Window**: `WINDOW_TITLE`, `WINDOW_SIZE`

## Platform-Specific Notes

### macOS
- FFmpeg and pngquant install easily via Homebrew
- Native file dialogs integrate seamlessly

### Windows
- See `WINDOWS_BUILD.md` for detailed build instructions
- May require manual FFmpeg installation and PATH configuration
- pngquant is optional but recommended

### Linux
- FFmpeg and pngquant available in most package managers
- Tested on Ubuntu 20.04+ and Debian 11+
- Some distributions may require additional GTK dependencies for CustomTkinter

## Dependencies

### Core Dependencies
- **customtkinter** (>=5.2.2) - Modern UI framework
- **Pillow** (>=12.0.0) - Image processing
- **ffmpeg-python** (>=0.2.0) - Python FFmpeg bindings
- **cairosvg** (>=2.8.2) - SVG support

### System Dependencies
- **ffmpeg** - Video processing (required)
- **pngquant** - Advanced PNG compression (optional but recommended)

See `DEPENDENCIES.md` for detailed installation instructions.

## Troubleshooting

### "FFmpeg not found" Error
- Ensure FFmpeg is installed and in your system PATH
- Test with: `ffmpeg -version`

### SVG Conversion Fails
- Install CairoSVG: `pip install cairosvg`
- On Linux, may need: `sudo apt install libcairo2-dev`

### PNG Compression Quality Poor
- Install pngquant for better results
- Application automatically falls back to Pillow if pngquant unavailable

### Video Compression Takes Long
- This is normal for high-quality encoding
- Monitor progress in the log files
- Consider adjusting `FFMPEG_PRESET` in constants.py (faster presets: fast, medium)

## License

This project is open source. See repository for license details.

## Credits

Built with:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky
- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [FFmpeg](https://ffmpeg.org/) - Multimedia framework
- [pngquant](https://pngquant.org/) - PNG optimization tool
