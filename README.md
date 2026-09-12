# Refiner

Convert and compress images and videos. No limits, no tracking.

**[Download](https://github.com/lloydturnercreate/Refiner/releases)** · **[Website](https://getrefiner.vercel.app)**

## Formats

**Images** — PNG, JPG, WebP, AVIF, SVG, BMP
**Videos** — MP4, WebM, MOV, GIF

## Install

Download `Refiner-macOS.zip` from [Releases](https://github.com/lloydturnercreate/Refiner/releases), unzip, and drag to Applications.

macOS may block the first launch — right-click the app, choose Open, then click Open again. Or run `xattr -cr Refiner.app` in Terminal.

### Prerequisites (for running from source)

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) (`brew install ffmpeg`)
- [pngquant](https://pngquant.org/) (optional, `brew install pngquant`)

```bash
pip install -r requirements.txt
python main.py
```

## Building

```bash
pip install -r requirements-dev.txt
python build.py
```

Output: `dist/Refiner.app` (macOS)

## Credits

Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), [Pillow](https://python-pillow.org/), [FFmpeg](https://ffmpeg.org/), and [pngquant](https://pngquant.org/).

Made by [Lloyd Turner](https://github.com/lloydturnercreate).
