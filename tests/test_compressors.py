"""
Tests for compressors.py — image compression using in-memory test images.
Video compression requires a live FFmpeg binary and is skipped when unavailable.
"""

import os
import shutil
import tempfile
import pytest
from PIL import Image

from compressors import (
    ImageCompressor,
    CompressorFactory,
    CompressionError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_image(path: str, mode: str = "RGB", size=(64, 64), color=(100, 149, 237)):
    img = Image.new(mode, size, color)
    img.save(path)


# ---------------------------------------------------------------------------
# ImageCompressor
# ---------------------------------------------------------------------------

class TestImageCompressor:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.compressor = ImageCompressor()

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_compress_jpg(self):
        src = os.path.join(self.tmp, "input.jpg")
        dst = os.path.join(self.tmp, "output.jpg")
        _make_test_image(src)
        self.compressor.compress(src, dst, compression_level=50)
        assert os.path.exists(dst)
        assert os.path.getsize(dst) > 0

    def test_compress_png(self):
        src = os.path.join(self.tmp, "input.png")
        dst = os.path.join(self.tmp, "output.png")
        _make_test_image(src)
        self.compressor.compress(src, dst, compression_level=50)
        assert os.path.exists(dst)
        assert os.path.getsize(dst) > 0

    def test_compress_webp(self):
        src = os.path.join(self.tmp, "input.webp")
        dst = os.path.join(self.tmp, "output.webp")
        _make_test_image(src)
        self.compressor.compress(src, dst, compression_level=50)
        assert os.path.exists(dst)

    def test_bmp_raises_compression_error(self):
        """BMP has no compression; should raise with a clear message."""
        src = os.path.join(self.tmp, "input.bmp")
        dst = os.path.join(self.tmp, "output.bmp")
        _make_test_image(src)
        with pytest.raises(CompressionError, match="BMP files cannot be compressed"):
            self.compressor.compress(src, dst, compression_level=50)

    def test_unsupported_format_raises(self):
        src = os.path.join(self.tmp, "input.svg")
        dst = os.path.join(self.tmp, "output.svg")
        with open(src, "w") as f:
            f.write('<svg/>')
        with pytest.raises(CompressionError):
            self.compressor.compress(src, dst, compression_level=50)

    def test_higher_level_produces_smaller_jpg(self):
        """More aggressive compression should reduce file size."""
        src = os.path.join(self.tmp, "input.jpg")
        low_dst = os.path.join(self.tmp, "low.jpg")
        high_dst = os.path.join(self.tmp, "high.jpg")
        # Use a photo-like image (gradient) for more realistic compression delta
        img = Image.new("RGB", (256, 256))
        pixels = img.load()
        for x in range(256):
            for y in range(256):
                pixels[x, y] = (x, y, (x + y) % 256)
        img.save(src)
        self.compressor.compress(src, low_dst, compression_level=10)
        self.compressor.compress(src, high_dst, compression_level=90)
        assert os.path.getsize(high_dst) < os.path.getsize(low_dst)

    def test_simulate_jpg_returns_int(self):
        src = os.path.join(self.tmp, "input.jpg")
        _make_test_image(src)
        result = self.compressor.simulate_compression(src, 50)
        assert isinstance(result, int)
        assert result > 0

    def test_simulate_png_returns_int(self):
        src = os.path.join(self.tmp, "input.png")
        _make_test_image(src)
        result = self.compressor.simulate_compression(src, 50)
        assert isinstance(result, int)
        assert result > 0

    def test_calculate_quality_bounds(self):
        """Quality must stay within min/max at both ends of the slider."""
        q_min = self.compressor._calculate_quality(100)
        q_max = self.compressor._calculate_quality(0)
        assert 0 < q_min <= q_max <= 100

    def test_calculate_png_quality_range_bounds(self):
        lo_min, lo_max = self.compressor._calculate_png_quality_range(0)
        hi_min, hi_max = self.compressor._calculate_png_quality_range(100)
        assert lo_min <= lo_max
        assert hi_min <= hi_max
        assert hi_min <= lo_min  # more compression → lower quality floor


# ---------------------------------------------------------------------------
# CompressorFactory
# ---------------------------------------------------------------------------

class TestCompressorFactory:
    def test_image_path_returns_image_compressor(self):
        compressor = CompressorFactory.create_compressor("photo.jpg")
        assert isinstance(compressor, ImageCompressor)

    def test_unsupported_raises(self):
        with pytest.raises(CompressionError):
            CompressorFactory.create_compressor("document.pdf")
