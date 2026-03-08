"""
Tests for utils.py — all pure functions, no I/O except validate_file_path.
"""

import os
import tempfile
import pytest

from utils import (
    normalize_extension,
    convert_size,
    get_file_type,
    is_supported_format,
    get_valid_output_formats,
    generate_output_filename,
    validate_file_path,
)


class TestNormalizeExtension:
    def test_already_lowercase_with_dot(self):
        assert normalize_extension(".png") == ".png"

    def test_uppercase_converted(self):
        assert normalize_extension(".PNG") == ".png"

    def test_no_leading_dot_added(self):
        assert normalize_extension("jpg") == ".jpg"

    def test_jpeg_unified_to_jpg(self):
        assert normalize_extension(".jpeg") == ".jpg"
        assert normalize_extension(".JPEG") == ".jpg"

    def test_other_extensions_unchanged(self):
        assert normalize_extension(".webp") == ".webp"
        assert normalize_extension(".mp4") == ".mp4"


class TestConvertSize:
    def test_zero(self):
        assert convert_size(0) == "0B"

    def test_bytes(self):
        assert convert_size(512) == "512.0B"

    def test_kilobytes(self):
        assert convert_size(1024) == "1.0KB"

    def test_megabytes(self):
        assert convert_size(1024 * 1024) == "1.0MB"

    def test_gigabytes(self):
        assert convert_size(1024 ** 3) == "1.0GB"

    def test_fractional(self):
        result = convert_size(1536)  # 1.5 KB
        assert result == "1.5KB"


class TestGetFileType:
    def test_image_types(self):
        for ext in [".png", ".jpg", ".webp", ".avif", ".bmp"]:
            assert get_file_type(f"file{ext}") == "image", f"Failed for {ext}"

    def test_video_types(self):
        for ext in [".mp4", ".webm", ".mov", ".gif"]:
            assert get_file_type(f"file{ext}") == "video", f"Failed for {ext}"

    def test_unknown_type(self):
        assert get_file_type("file.txt") == "unknown"
        assert get_file_type("file.pdf") == "unknown"

    def test_case_insensitive(self):
        assert get_file_type("FILE.PNG") == "image"
        assert get_file_type("video.MP4") == "video"


class TestIsSupportedFormat:
    def test_supported_image(self):
        assert is_supported_format("photo.jpg") is True
        assert is_supported_format("icon.png") is True

    def test_supported_video(self):
        assert is_supported_format("clip.mp4") is True

    def test_unsupported(self):
        assert is_supported_format("doc.pdf") is False
        assert is_supported_format("data.csv") is False


class TestGetValidOutputFormats:
    def test_image_excludes_self(self):
        formats = get_valid_output_formats("photo.png")
        assert ".png" not in formats
        assert ".jpg" in formats
        assert ".webp" in formats

    def test_video_excludes_self(self):
        formats = get_valid_output_formats("clip.mp4")
        assert ".mp4" not in formats
        assert ".webm" in formats
        assert ".gif" in formats

    def test_returns_list(self):
        assert isinstance(get_valid_output_formats("photo.jpg"), list)


class TestGenerateOutputFilename:
    def test_default_suffix(self):
        result = generate_output_filename("/tmp/photo.jpg")
        assert result == "/tmp/photo-min.jpg"

    def test_custom_suffix(self):
        result = generate_output_filename("/tmp/clip.mp4", suffix="-compressed")
        assert result == "/tmp/clip-compressed.mp4"

    def test_preserves_directory(self):
        result = generate_output_filename("/Users/me/docs/image.png")
        assert result.startswith("/Users/me/docs/")


class TestValidateFilePath:
    def test_empty_string(self):
        valid, msg = validate_file_path("")
        assert valid is False
        assert msg is not None

    def test_nonexistent_path(self):
        valid, msg = validate_file_path("/nonexistent/path/file.png")
        assert valid is False
        assert "does not exist" in msg

    def test_directory_not_file(self):
        valid, msg = validate_file_path(tempfile.gettempdir())
        assert valid is False
        assert "not a file" in msg

    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            tmp_path = f.name
        try:
            valid, msg = validate_file_path(tmp_path)
            assert valid is True
            assert msg is None
        finally:
            os.unlink(tmp_path)
