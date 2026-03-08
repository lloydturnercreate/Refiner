"""
Compressors for images and videos with adjustable quality.
"""

import os
import io
import tempfile
import subprocess
from PIL import Image
import ffmpeg

from constants import (
    IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, COMPRESSION_QUALITY_RANGE
)
from utils import normalize_extension


class CompressionError(Exception):
    """Raised when a compression operation fails."""


class BaseCompressor:
    """Abstract compressor interface for files."""
    
    def compress(self, input_path: str, output_path: str, compression_level: int) -> None:
        """Compress file at input_path to output_path using compression_level (0-100)."""
        raise NotImplementedError("Subclasses must implement compress method")
    
    def simulate_compression(self, input_path: str, compression_level: int) -> int:
        """Return predicted output size in bytes for a given compression_level."""
        raise NotImplementedError("Subclasses must implement simulate_compression method")


class ImageCompressor(BaseCompressor):
    """Image compression for JPEG/WebP/AVIF/PNG/BMP using Pillow and pngquant."""
    
    def compress(self, input_path: str, output_path: str, compression_level: int) -> None:
        """Compress an image to the format implied by output_path."""
        ext = normalize_extension(os.path.splitext(input_path)[1])
        
        if ext in ['.jpg', '.webp', '.avif']:
            self._compress_jpeg_webp_avif(input_path, output_path, compression_level)
        elif ext == '.png':
            self._compress_png(input_path, output_path, compression_level)
        elif ext == '.bmp':
            self._compress_bmp(input_path, output_path, compression_level)
        else:
            raise CompressionError(f"Unsupported image format: {ext}")
    
    def simulate_compression(self, input_path: str, compression_level: int) -> int:
        """Predict compressed size in bytes for the image at input_path."""
        ext = normalize_extension(os.path.splitext(input_path)[1])
        
        if ext in ['.jpg', '.webp', '.avif', '.bmp']:
            return self._simulate_jpeg_webp_avif_bmp(input_path, compression_level)
        elif ext == '.png':
            return self._simulate_png(input_path, compression_level)
        else:
            return os.path.getsize(input_path)
    
    def _compress_jpeg_webp_avif(self, input_path: str, output_path: str, compression_level: int) -> None:
        """Compress JPEG/WebP/AVIF using Pillow quality mapping."""
        quality = self._calculate_quality(compression_level)
        
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "LA") and output_path.lower().endswith('.jpg'):
                img = img.convert("RGB")
            ext = normalize_extension(os.path.splitext(output_path)[1])
            if ext == '.jpg':
                format_name = "JPEG"
            elif ext == '.webp':
                format_name = "WEBP"
            elif ext == '.avif':
                format_name = "AVIF"
            else:
                format_name = "JPEG"
            
            img.save(output_path, format=format_name, quality=quality)
    
    def _compress_png(self, input_path: str, output_path: str, compression_level: int) -> None:
        """Compress PNG via pngquant when available, otherwise Pillow optimize."""
        try:
            q_min, q_max = self._calculate_png_quality_range(compression_level)
            subprocess.run([
                "pngquant", f"--quality={q_min}-{q_max}", "--force",
                "--output", output_path, input_path
            ], check=True, capture_output=True, timeout=30)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self._compress_png_pil(input_path, output_path, compression_level)

    def _compress_png_pil(self, input_path: str, output_path: str, compression_level: int) -> None:
        """Fallback PNG compression using Pillow — maps slider to zlib compress_level (0–9)."""
        compress_level = int(compression_level / 100 * 9)
        with Image.open(input_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            img.save(output_path, format="PNG", optimize=True, compress_level=compress_level)
    
    def _compress_bmp(self, input_path: str, output_path: str, compression_level: int) -> None:
        """Re-save a BMP file. BMP is always uncompressed; quality has no effect.

        Raises CompressionError to surface a clear message to the user rather
        than silently producing an identical file.
        """
        raise CompressionError(
            "BMP files cannot be compressed — the format does not support it. "
            "Convert to PNG or JPEG first, then compress."
        )
    
    def _simulate_jpeg_webp_avif_bmp(self, input_path: str, compression_level: int) -> int:
        """Estimate compressed size for JPEG/WebP/AVIF/BMP by encoding to a buffer."""
        quality = self._calculate_quality(compression_level)
        
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
            
            buf = io.BytesIO()
            ext = normalize_extension(os.path.splitext(input_path)[1])
            
            if ext == '.jpg':
                img.save(buf, format="JPEG", quality=quality)
            elif ext == '.webp':
                img.save(buf, format="WEBP", quality=quality)
            elif ext == '.avif':
                img.save(buf, format="AVIF", quality=quality)
            elif ext == '.bmp':
                img.save(buf, format="BMP", quality=quality)
            else:
                img.save(buf, format="JPEG", quality=quality)
            
            return len(buf.getvalue())
    
    def _simulate_png(self, input_path: str, compression_level: int) -> int:
        """Estimate compressed size for PNG using pngquant or Pillow."""
        try:
            q_min, q_max = self._calculate_png_quality_range(compression_level)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_name = tmp.name
            
            subprocess.run([
                "pngquant", f"--quality={q_min}-{q_max}", "--force", 
                "--output", tmp_name, input_path
            ], check=True, capture_output=True, timeout=30)
            
            size = os.path.getsize(tmp_name)
            os.remove(tmp_name)
            return size
        except Exception:
            with Image.open(input_path) as img:
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                buf = io.BytesIO()
                img.save(buf, format="PNG", optimize=True)
                return len(buf.getvalue())
    
    def _calculate_quality(self, compression_level: int) -> int:
        """Map slider level (0-100) to Pillow quality (100 at 0, 30 at 100)."""
        min_quality = COMPRESSION_QUALITY_RANGE['min_quality']
        max_quality = COMPRESSION_QUALITY_RANGE['max_quality']
        quality = max_quality - (max_quality - min_quality) * (compression_level / 100)
        return int(max(min_quality, min(max_quality, quality)))
    
    def _calculate_png_quality_range(self, compression_level: int) -> tuple[int, int]:
        """Return (min,max) pngquant quality values derived from compression_level.

        At level 0 (no compression): 100-100 (lossless).
        At level 100 (max compression): 60-65.
        """
        q_min = int(100 - (40 * compression_level / 100))
        q_max = int(100 - (35 * compression_level / 100))
        q_min = max(60, min(100, q_min))
        q_max = max(65, min(100, q_max))

        return q_min, q_max


class VideoCompressor(BaseCompressor):
    """Video compression using ffmpeg with bitrate targeting and GIF palette path."""

    def compress(self, input_path: str, output_path: str, compression_level: int,
                 target_fps: float = None) -> None:
        """Compress a video file using a target bitrate derived from compression_level."""
        ext = normalize_extension(os.path.splitext(input_path)[1])

        if ext == '.gif':
            self._compress_gif(input_path, output_path, compression_level, target_fps)
            return
        
        try:
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
        except Exception as e:
            raise CompressionError(f"Failed to get video duration: {str(e)}")
        
        original_size = os.path.getsize(input_path)
        original_bitrate = (original_size * 8) / duration
        compression_factor = COMPRESSION_QUALITY_RANGE['video_compression_factor']
        target_bitrate = int(original_bitrate * (1 - compression_level/100 * compression_factor))
        target_bitrate_str = f"{int(target_bitrate/1000)}k"
        
        try:
            ffmpeg.input(input_path).output(
                output_path, 
                b=target_bitrate_str
            ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            raise CompressionError(f"Video compression failed: {str(e)}")
    
    def _compress_gif(self, input_path: str, output_path: str,
                      compression_level: int, target_fps: float = None) -> None:
        """Compress a GIF with palette reduction and optional FPS targeting."""
        try:
            max_colors = int(256 - (compression_level / 100 * 240))
            max_colors = max(16, min(256, max_colors))

            fps_filter = f"fps={target_fps}," if target_fps else ""
            vf = (
                f"{fps_filter}"
                f"split[s0][s1];"
                f"[s0]palettegen=max_colors={max_colors}[p];"
                f"[s1][p]paletteuse=dither=bayer:bayer_scale=5"
            )

            subprocess.run(
                ["ffmpeg", "-i", input_path, "-vf", vf, "-loop", "0", "-y", output_path],
                check=True, capture_output=True, timeout=120,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            raise CompressionError(f"GIF compression failed: {str(e)}")
    
    def simulate_compression(self, input_path: str, compression_level: int,
                             target_fps: float = None) -> int:
        """Predict compressed size in bytes for a video at input_path."""
        ext = normalize_extension(os.path.splitext(input_path)[1])

        if ext == '.gif':
            original_size = os.path.getsize(input_path)
            # Palette reduction (256→16 colors) with LZW + bayer dither typically
            # achieves 15–25% size reduction in practice — not the 50% a naive
            # linear model suggests. Use 0.25 as a conservative max reduction.
            color_factor = 1.0 - (compression_level / 100 * 0.25)
            if target_fps is not None:
                original_fps = self._get_source_fps(input_path)
                fps_factor = min(1.0, target_fps / original_fps) if original_fps > 0 else 1.0
            else:
                fps_factor = 1.0
            return int(original_size * color_factor * fps_factor)

        original_size = os.path.getsize(input_path)
        compression_factor = COMPRESSION_QUALITY_RANGE['video_compression_factor']
        predicted = original_size * (1 - compression_level/100 * compression_factor)
        return int(predicted)

    def _get_source_fps(self, input_path: str) -> float:
        """Return source video/GIF frames-per-second via ffprobe."""
        try:
            from fractions import Fraction
            probe = ffmpeg.probe(input_path)
            stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            if stream and 'r_frame_rate' in stream:
                return float(Fraction(stream['r_frame_rate']))
        except Exception:
            pass
        return 15.0


class CompressorFactory:
    """Factory for selecting an appropriate compressor for a given file type."""
    
    @staticmethod
    def create_compressor(input_path: str) -> BaseCompressor:
        """Return a compressor instance suitable for the file at input_path."""
        ext = normalize_extension(os.path.splitext(input_path)[1])
        
        if ext in IMAGE_EXTENSIONS:
            return ImageCompressor()
        elif ext in VIDEO_EXTENSIONS:
            return VideoCompressor()
        else:
            raise CompressionError(f"Unsupported file type for compression: {ext}")


def compress_file(input_path: str, output_path: str, compression_level: int,
                  target_fps: float = None) -> None:
    """Compress a file by delegating to a type-appropriate compressor."""
    compressor = CompressorFactory.create_compressor(input_path)
    if isinstance(compressor, VideoCompressor):
        compressor.compress(input_path, output_path, compression_level, target_fps)
    else:
        compressor.compress(input_path, output_path, compression_level)


def simulate_compression(input_path: str, compression_level: int,
                         target_fps: float = None) -> int:
    """Predict output size in bytes for a compressed file.

    A 15% buffer is added so predictions err on the high side — better for
    users to be pleasantly surprised than to exceed their expected file size.
    """
    compressor = CompressorFactory.create_compressor(input_path)
    if isinstance(compressor, VideoCompressor):
        raw = compressor.simulate_compression(input_path, compression_level, target_fps)
    else:
        raw = compressor.simulate_compression(input_path, compression_level)
    return int(raw * 1.15)
