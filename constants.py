"""
Centralized constants for formats, codecs, and UI configuration.
"""

# File format definitions
IMAGE_EXTENSIONS = ['.png', '.jpg', '.webp', '.avif', '.svg', '.bmp']
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.mov', '.gif']
AVAILABLE_FORMATS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS

# Compression settings
COMPRESSION_QUALITY_RANGE = {
    'min_quality': 30,  # Increased from 20 to avoid visible artifacts
    'max_quality': 100,  # Increased from 95 to support lossless
    'quality_reduction_factor': 0.70,  # Adjust for better distribution
    'png_quality_min_reduction': 0.7,  # Improved PNG quality range
    'png_quality_max_reduction': 0.65,  # Better max quality for PNG
    'video_compression_factor': 0.75
}

# Video conversion settings
DEFAULT_FPS = 15.0
MAX_FPS = 60.0

# FFmpeg settings
FFMPEG_CRF = 18
FFMPEG_PRESET = "slow"
WEBM_CRF = 30
# UI settings
WINDOW_TITLE = "Refiner - Img/Video Converter & Compressor"
WINDOW_SIZE = "450x580"
WINDOW_RESIZABLE = False

# UI colors and themes
APPEARANCE_MODE = "dark"
COLOR_THEME = "dark-blue"

# Apple-inspired dark palette
BACKGROUND_PRIMARY = "#000000"      # Pure black window bg
BACKGROUND_SECONDARY = "#1C1C1E"    # Dark grouped background
SURFACE_PRIMARY = "#1C1C1E"         # Card background
SURFACE_SECONDARY = "#2C2C2E"       # Input / secondary surface
SURFACE_ELEVATED = "#3A3A3C"        # Hover / raised elements

# Text
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#8E8E93"          # Apple secondary label
TEXT_MUTED = "#636366"              # Tertiary label

# Accent
ACCENT_PRIMARY = "#FF6600"          # Orange
ACCENT_SECONDARY = "#E05500"        # Darker orange hover
ACCENT_SUCCESS = "#32D74B"          # iOS green
ACCENT_WARNING = "#FF9F0A"          # iOS amber
ACCENT_ERROR = "#FF453A"            # iOS red

# Borders / separators
BORDER_PRIMARY = "#38383A"          # Apple hairline separator
BORDER_SECONDARY = "#48484A"

# Typography
import platform as _platform
_system = _platform.system()
if _system == "Darwin":
    FONT_FAMILY = "Helvetica Neue"
elif _system == "Windows":
    FONT_FAMILY = "Segoe UI"
else:
    FONT_FAMILY = "DejaVu Sans"
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_XLARGE = 18
FONT_SIZE_XXLARGE = 24

# Spacing
SPACING_XS = 6
SPACING_SM = 12
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32
SPACING_XXL = 40

# Border radius
RADIUS_SM = 6
RADIUS_MD = 8
RADIUS_LG = 12
RADIUS_XL = 16

# File dialog settings
DEFAULT_EXTENSION = ".png"

# Prediction update delay (milliseconds)
PREDICTION_UPDATE_DELAY = 500

CONTAINER_FG_COLOR = BACKGROUND_SECONDARY
FRAME_FG_COLOR = SURFACE_PRIMARY
TEXT_COLOR = TEXT_PRIMARY
ACCENT_COLOR = ACCENT_PRIMARY
