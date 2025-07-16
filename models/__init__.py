"""
Models package for Box Packer application.

This package contains the core data models representing boxes and pallets.
"""

from .box import Box
from .pallet import Pallet

__all__ = ['Box', 'Pallet']
__version__ = "1.0.0"
