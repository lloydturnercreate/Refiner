"""
Tests for converters.py — image conversions using in-memory test images.
Video conversion requires a live FFmpeg binary so those are skipped in CI
unless the binary is available.
"""

import os
import tempfile
import shutil
import pytest
from PIL import Image

from converters import (
    ImageConverter,
    SVGConverter,
    ConverterFactory,
    ConversionError,
    SVG_AVAILABLE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_image(path: str, mode: str = "RGB", size=(32, 32), color=(100, 149, 237)):
    """Write a small solid-color image to path."""
    img = Image.new(mode, size, color)
    img.save(path)


# ---------------------------------------------------------------------------
# ImageConverter
# ---------------------------------------------------------------------------

class TestImageConverter:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.converter = ImageConverter()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_png_to_jpg(self):
        src = os.path.join(self.tmp, "input.png")
        dst = os.path.join(self.tmp, "output.jpg")
        _make_test_image(src)
        self.converter.convert(src, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.format == "JPEG"

    def test_jpg_to_png(self):
        src = os.path.join(self.tmp, "input.jpg")
        dst = os.path.join(self.tmp, "output.png")
        _make_test_image(src)
        self.converter.convert(src, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.format == "PNG"

    def test_png_to_webp(self):
        src = os.path.join(self.tmp, "input.png")
        dst = os.path.join(self.tmp, "output.webp")
        _make_test_image(src)
        self.converter.convert(src, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.format == "WEBP"

    def test_rgba_to_jpg_strips_alpha(self):
        """RGBA images must be converted to RGB before saving as JPEG."""
        src = os.path.join(self.tmp, "input.png")
        dst = os.path.join(self.tmp, "output.jpg")
        _make_test_image(src, mode="RGBA", color=(255, 0, 0, 128))
        self.converter.convert(src, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.mode == "RGB"

    def test_svg_input_raises(self):
        """SVG inputs must be routed to SVGConverter, not ImageConverter."""
        src = os.path.join(self.tmp, "input.svg")
        dst = os.path.join(self.tmp, "output.png")
        with open(src, "w") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"/>')
        with pytest.raises(ConversionError):
            self.converter.convert(src, dst)

    def test_missing_input_raises(self):
        with pytest.raises(ConversionError):
            self.converter.convert("/nonexistent/input.png", "/tmp/out.jpg")


# ---------------------------------------------------------------------------
# SVGConverter
# ---------------------------------------------------------------------------

SIMPLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">
  <rect width="32" height="32" fill="blue"/>
</svg>"""


@pytest.mark.skipif(not SVG_AVAILABLE, reason="cairosvg not installed")
class TestSVGConverter:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.converter = SVGConverter()
        self.svg_path = os.path.join(self.tmp, "input.svg")
        with open(self.svg_path, "w") as f:
            f.write(SIMPLE_SVG)

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_svg_to_png(self):
        dst = os.path.join(self.tmp, "output.png")
        self.converter.convert(self.svg_path, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.format == "PNG"

    def test_svg_to_jpg(self):
        dst = os.path.join(self.tmp, "output.jpg")
        self.converter.convert(self.svg_path, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.format == "JPEG"

    def test_svg_to_webp(self):
        dst = os.path.join(self.tmp, "output.webp")
        self.converter.convert(self.svg_path, dst)
        assert os.path.exists(dst)
        with Image.open(dst) as img:
            assert img.format == "WEBP"


# ---------------------------------------------------------------------------
# ConverterFactory
# ---------------------------------------------------------------------------

class TestConverterFactory:
    def test_image_to_image_returns_image_converter(self):
        converter = ConverterFactory.create_converter("photo.png", "photo.jpg")
        assert isinstance(converter, ImageConverter)

    def test_svg_to_image_returns_svg_converter_if_available(self):
        converter = ConverterFactory.create_converter("icon.svg", "icon.png")
        if SVG_AVAILABLE:
            assert isinstance(converter, SVGConverter)
        else:
            assert isinstance(converter, ImageConverter)

    def test_unsupported_raises(self):
        with pytest.raises(ConversionError):
            ConverterFactory.create_converter("file.txt", "file.doc")
