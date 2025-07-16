"""
Configuration constants for the Box Packer application.

This module contains all the configuration parameters and constants
used throughout the box packing system.
"""

# Pallet configuration constants
PALLET_WIDTH: float = 40.0    # Standard pallet width in inches
PALLET_LENGTH: float = 48.0   # Standard pallet length in inches
TARGET_RATIO: float = 6.0 / 5.0  # Target rows/columns ratio (length/width) for optimal stability
PALLET_RATIO: float = PALLET_WIDTH / PALLET_LENGTH  # 0.83 for maintaining proportions during scaling

# Scaling configuration
DEFAULT_SCALE_INCREMENT: float = 0.1  # Increment for pallet scaling
MAX_SCALE_FACTOR: float = 3.0        # Maximum scale factor allowed

# Input validation constants
MAX_REASONABLE_BOXES: int = 100  # Maximum reasonable number of boxes for validation
MIN_DIMENSION: float = 0.1       # Minimum box dimension in inches
MAX_DIMENSION: float = 100.0     # Maximum box dimension in inches
