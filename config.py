"""
Configuration constants for the Box Packer application.

This module contains all the configuration parameters and constants
used throughout the box packing system.
"""

# Pallet configuration constants
PALLET_WIDTH = 40    # Standard pallet width in inches
PALLET_LENGTH = 48   # Standard pallet length in inches
TARGET_RATIO = 6 / 5 # Target rows/columns ratio (length/width) for optimal stability
PALLET_RATIO = PALLET_WIDTH / PALLET_LENGTH  # 0.83 for maintaining proportions during scaling

# Scaling configuration
DEFAULT_SCALE_INCREMENT = 0.1  # Increment for pallet scaling
MAX_SCALE_FACTOR = 3.0        # Maximum scale factor allowed
