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

# macOS-native dark palette
BACKGROUND_PRIMARY = "#2D2D30"      # Window background
BACKGROUND_SECONDARY = "#2D2D30"    # Same — no card distinction
SURFACE_PRIMARY = "#2D2D30"         # Flat (invisible cards)
SURFACE_SECONDARY = "#3A3A3C"       # Input / control backgrounds
SURFACE_ELEVATED = "#444446"        # Hover / raised elements
PREVIEW_BACKGROUND = "#222224"      # Dark inset for preview area

# Text
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#98989D"          # macOS secondary label
TEXT_MUTED = "#636366"              # Tertiary label
TEXT_INFO = "#4A4A4E"               # Conversion info, subtle

# Accent — used sparingly
ACCENT_PRIMARY = "#FF6600"          # Orange (logo, action button, slider, progress)
ACCENT_SECONDARY = "#E85D00"        # Darker orange hover
ACCENT_SUCCESS = "#30D158"          # macOS green
ACCENT_WARNING = "#FF9F0A"          # macOS amber
ACCENT_ERROR = "#FF453A"            # macOS red

# Borders / separators
BORDER_PRIMARY = "#3A3A3C"          # Subtle separator
BORDER_SECONDARY = "#3F3F41"        # Button border

# Tab control (native gray, no accent)
TAB_BG = "#373739"
TAB_SELECTED = "#444446"
TAB_UNSELECTED = "#373739"
TAB_TEXT_ACTIVE = "#FFFFFF"
TAB_TEXT_INACTIVE = "#7C7C80"

# Ghost buttons (Browse)
GHOST_BG = "#3A3A3C"
GHOST_HOVER = "#444446"
GHOST_TEXT = "#AEAEB2"

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
RADIUS_SM = 4
RADIUS_MD = 6
RADIUS_LG = 8
RADIUS_XL = 10

# File dialog settings
DEFAULT_EXTENSION = ".png"

# Prediction update delay (milliseconds)
PREDICTION_UPDATE_DELAY = 500

CONTAINER_FG_COLOR = BACKGROUND_SECONDARY
FRAME_FG_COLOR = SURFACE_PRIMARY
TEXT_COLOR = TEXT_PRIMARY
ACCENT_COLOR = ACCENT_PRIMARY
