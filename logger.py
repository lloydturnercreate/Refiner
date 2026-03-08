"""
Centralized logging setup for the application.
"""

import logging
import os
import platform
from datetime import datetime
from typing import Optional


def _get_log_directory() -> str:
    """Return a platform-appropriate, user-writable log directory."""
    system = platform.system()
    if system == "Darwin":
        base = os.path.expanduser("~/Library/Logs")
    elif system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
    return os.path.join(base, "Refiner", "logs")


class RefinerLogger:
    """Thin wrapper around logging with console and daily file handlers."""
    
    def __init__(self, name: str = "refiner", log_level: int = logging.INFO):
        """Initialize named logger with stream and file handlers."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Attach console and rotating daily file handlers."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        log_dir = _get_log_directory()
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"refiner_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log a critical message."""
        self.logger.critical(message)
    
    def log_conversion_start(self, input_path: str, output_path: str) -> None:
        """Log the start of a conversion."""
        self.info(f"Starting conversion: {input_path} -> {output_path}")
    
    def log_conversion_success(self, input_path: str, output_path: str) -> None:
        """Log a successful conversion."""
        self.info(f"Conversion successful: {input_path} -> {output_path}")
    
    def log_conversion_error(self, input_path: str, output_path: str, error: str) -> None:
        """Log a failed conversion."""
        self.error(f"Conversion failed: {input_path} -> {output_path}, Error: {error}")
    
    def log_compression_start(self, input_path: str, output_path: str, level: int) -> None:
        """Log the start of a compression run."""
        self.info(f"Starting compression: {input_path} -> {output_path} (level: {level})")
    
    def log_compression_success(self, input_path: str, output_path: str, 
                               original_size: int, compressed_size: int) -> None:
        """Log a successful compression with reduction percentage."""
        compression_ratio = (1 - compressed_size / original_size) * 100
        self.info(f"Compression successful: {input_path} -> {output_path} "
                f"(reduced by {compression_ratio:.1f}%)")
    
    def log_compression_error(self, input_path: str, output_path: str, error: str) -> None:
        """Log a failed compression."""
        self.error(f"Compression failed: {input_path} -> {output_path}, Error: {error}")


# Global logger instance
logger = RefinerLogger()
