"""
Converters for transforming images and videos between supported formats.
"""

import os
import tempfile
from typing import Optional
from PIL import Image
import ffmpeg
from fractions import Fraction

try:
    import cairosvg
    SVG_AVAILABLE = True
except (ImportError, OSError):
    SVG_AVAILABLE = False
    cairosvg = None

from constants import (
    IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, DEFAULT_FPS, MAX_FPS,
    FFMPEG_CRF, FFMPEG_PRESET, WEBM_CRF
)
from utils import normalize_extension, get_file_type


class ConversionError(Exception):
    """Raised when a conversion operation fails."""
    pass


class BaseConverter:
    """Abstract converter interface for files."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert file at input_path to output_path."""
        raise NotImplementedError("Subclasses must implement convert method")


class ImageConverter(BaseConverter):
    """Image format conversions using Pillow and optional CairoSVG for SVG."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert an image to the format implied by output_path."""
        try:
            input_ext = normalize_extension(os.path.splitext(input_path)[1])
            if input_ext == '.svg':
                raise ConversionError("SVG support requires cairosvg. Install it with: pip install cairosvg")
            with Image.open(input_path) as img:
                if img.mode == "RGBA" and output_path.lower().endswith(".jpg"):
                    img = img.convert("RGB")
                output_format = self._get_output_format(output_path)
                img.save(output_path, format=output_format)

        except ConversionError:
            raise
        except Exception as e:
            raise ConversionError(f"Image conversion failed: {str(e)}")
    
    def _get_output_format(self, output_path: str) -> str:
        """Map file extension from output_path to Pillow format string."""
        ext = normalize_extension(os.path.splitext(output_path)[1])
        
        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.webp': 'WEBP',
            '.avif': 'AVIF',
            '.bmp': 'BMP'
        }
        
        return format_map.get(ext, 'PNG')


class VideoConverter(BaseConverter):
    """Video format conversions via ffmpeg/ffmpeg-python."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert a video to the format implied by output_path."""
        input_ext = normalize_extension(os.path.splitext(input_path)[1])
        output_ext = normalize_extension(os.path.splitext(output_path)[1])
        if input_ext == '.gif':
            self._convert_gif_to_video(input_path, output_path)
            return
        if output_ext == '.gif':
            self._convert_to_gif(input_path, output_path)
        elif output_ext == '.webm':
            self._convert_to_webm(input_path, output_path)
        elif input_path.lower().endswith('.mov'):
            self._convert_from_mov(input_path, output_path)
        else:
            self._convert_to_mp4(input_path, output_path)
    
    def _convert_to_gif(self, input_path: str, output_path: str) -> None:
        """Convert a video to GIF using palette optimisation.

        Uses a single-pass filtergraph with split so both palettegen and
        paletteuse share the same scaled stream — avoiding the 'multiple
        outgoing edges' error that ffmpeg-python's filter builder produces.
        """
        import subprocess
        try:
            fps = self._get_video_fps(input_path)
            target_fps = min(fps, MAX_FPS)
            vf = (
                f"fps={target_fps},"
                f"scale=iw:-1:flags=lanczos,"
                f"split[s0][s1];"
                f"[s0]palettegen[p];"
                f"[s1][p]paletteuse"
            )
            result = subprocess.run(
                ["ffmpeg", "-i", input_path, "-vf", vf, "-loop", "0", "-y", output_path],
                check=True, capture_output=True, timeout=120,
            )
        except subprocess.CalledProcessError as e:
            raise ConversionError(f"GIF conversion failed: {e.stderr.decode(errors='replace')}")
        except subprocess.TimeoutExpired:
            raise ConversionError("GIF conversion timed out")
    
    def _convert_to_webm(self, input_path: str, output_path: str) -> None:
        """Convert a video to WebM (VP9)."""
        try:
            ffmpeg.input(input_path).output(
                output_path, 
                vcodec='libvpx-vp9', 
                crf=WEBM_CRF, 
                b='0'
            ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            raise ConversionError(f"WebM conversion failed: {str(e)}")
    
    def _convert_from_mov(self, input_path: str, output_path: str) -> None:
        """Convert MOV to MP4/MOV, copying H.264 when possible."""
        try:
            codec = self._get_video_codec(input_path)
            if codec == "h264":
                ffmpeg.input(input_path).output(
                    output_path, 
                    codec='copy'
                ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            else:
                ffmpeg.input(input_path).output(
                    output_path, 
                    vcodec='libx264', 
                    crf=FFMPEG_CRF, 
                    preset=FFMPEG_PRESET
                ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
                
        except ffmpeg.Error as e:
            raise ConversionError(f"MOV conversion failed: {str(e)}")
    
    def _convert_to_mp4(self, input_path: str, output_path: str) -> None:
        """Convert a video to MP4 (H.264)."""
        try:
            ffmpeg.input(input_path).output(
                output_path, 
                vcodec='libx264', 
                crf=FFMPEG_CRF, 
                preset=FFMPEG_PRESET
            ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            raise ConversionError(f"MP4 conversion failed: {str(e)}")
    
    def _convert_gif_to_video(self, input_path: str, output_path: str) -> None:
        """Convert a GIF to MP4, WebM, or MOV."""
        try:
            output_ext = normalize_extension(os.path.splitext(output_path)[1])
            if output_ext == '.webm':
                ffmpeg.input(input_path).output(
                    output_path,
                    vcodec='libvpx-vp9',
                    crf=WEBM_CRF,
                    b='0'
                ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            else:
                ffmpeg.input(input_path).output(
                    output_path,
                    vcodec='libx264',
                    crf=FFMPEG_CRF,
                    preset=FFMPEG_PRESET
                ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
                
        except ffmpeg.Error as e:
            raise ConversionError(f"GIF to video conversion failed: {str(e)}")
    
    def _get_video_fps(self, input_path: str) -> float:
        """Return the source video's frames-per-second, defaulting when unknown."""
        try:
            probe = ffmpeg.probe(input_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream and 'r_frame_rate' in video_stream:
                fps_str = video_stream['r_frame_rate']
                return float(Fraction(fps_str))
            return DEFAULT_FPS
        except Exception:
            return DEFAULT_FPS
    
    def _get_video_codec(self, input_path: str) -> str:
        """Return the name of the source video's codec if detectable."""
        try:
            probe = ffmpeg.probe(input_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream and 'codec_name' in video_stream:
                return video_stream['codec_name']
            return "unknown"
        except Exception:
            return "unknown"


class SVGConverter(BaseConverter):
    """SVG to raster conversion using CairoSVG and Pillow."""
    
    def convert(self, input_path: str, output_path: str) -> None:
        """Convert an SVG to the raster format implied by output_path."""
        if not SVG_AVAILABLE:
            raise ConversionError("SVG support requires cairosvg. Install it with: pip install cairosvg")
        
        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_png.close()
        try:
            cairosvg.svg2png(url=input_path, write_to=temp_png.name)
            output_ext = normalize_extension(os.path.splitext(output_path)[1])
            if output_ext == '.png':
                os.rename(temp_png.name, output_path)
            else:
                with Image.open(temp_png.name) as img:
                    if img.mode == "RGBA" and output_path.lower().endswith(".jpg"):
                        img = img.convert("RGB")
                    output_format = self._get_output_format(output_path)
                    img.save(output_path, format=output_format)
        except ConversionError:
            raise
        except Exception as e:
            raise ConversionError(f"SVG conversion failed: {str(e)}")
        finally:
            if os.path.exists(temp_png.name):
                try:
                    os.unlink(temp_png.name)
                except OSError:
                    pass
    
    def _get_output_format(self, output_path: str) -> str:
        """Map file extension to a Pillow image format string."""
        ext = normalize_extension(os.path.splitext(output_path)[1])
        
        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.webp': 'WEBP',
            '.avif': 'AVIF',
            '.bmp': 'BMP'
        }
        
        return format_map.get(ext, 'PNG')


class ConverterFactory:
    """Factory for selecting the appropriate converter for a given input/output pair."""
    
    @staticmethod
    def create_converter(input_path: str, output_path: str) -> BaseConverter:
        """Return a converter instance suitable for the given file types."""
        input_ext = normalize_extension(os.path.splitext(input_path)[1])
        output_ext = normalize_extension(os.path.splitext(output_path)[1])
        if input_ext == '.svg' and output_ext in IMAGE_EXTENSIONS:
            if SVG_AVAILABLE:
                return SVGConverter()
            else:
                return ImageConverter()
        if input_ext in VIDEO_EXTENSIONS or output_ext in VIDEO_EXTENSIONS:
            return VideoConverter()
        if input_ext in IMAGE_EXTENSIONS or output_ext in IMAGE_EXTENSIONS:
            return ImageConverter()
        
        raise ConversionError(f"Unsupported conversion: {input_ext} to {output_ext}")


def convert_file(input_path: str, output_path: str) -> None:
    """Convert a file by delegating to a type-appropriate converter."""
    converter = ConverterFactory.create_converter(input_path, output_path)
    converter.convert(input_path, output_path)
