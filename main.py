"""
Application entry point.
"""

import os
import sys


def _configure_bundled_binaries() -> None:
    """When frozen by PyInstaller, prepend the imageio-ffmpeg binary dir to
    PATH so that ffmpeg-python and all subprocess calls find the bundled
    static ffmpeg/ffprobe without any system installation."""
    if not getattr(sys, "frozen", False):
        return
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        bin_dir = os.path.dirname(ffmpeg_exe)
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass  # fall back to system ffmpeg if available


_configure_bundled_binaries()

from ui_components import MainApplication  # noqa: E402
from logger import logger                  # noqa: E402


def main():
    """Start the UI application and handle top-level errors."""
    try:
        logger.info("Starting Refiner application")
        app = MainApplication()
        app.run()
        logger.info("Refiner application closed")
    except Exception as e:
        logger.critical(f"Fatal error in main application: {str(e)}")
        raise


if __name__ == "__main__":
    main()
