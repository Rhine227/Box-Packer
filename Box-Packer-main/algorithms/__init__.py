"""
Algorithms package for Box Packer application.

This package contains the core algorithms for box arrangement,
optimization, and pallet scaling.
"""

from .arrangement import generate_candidates, try_arrangement, find_best_arrangement_with_custom_pallet
from .optimization import auto_optimize_box_count, find_best_arrangement
from .scaling import find_best_arrangement_with_scaling

__all__ = [
    'generate_candidates', 'try_arrangement', 'find_best_arrangement_with_custom_pallet',
    'auto_optimize_box_count', 'find_best_arrangement',
    'find_best_arrangement_with_scaling'
]
