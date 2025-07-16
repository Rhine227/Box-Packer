"""
Utilities package for Box Packer application.

This package contains utility functions for input handling,
display formatting, geometric calculations, and visualization.
"""

from .input_handler import get_user_input
from .display import (
    print_arrangement, print_program_header, print_box_info,
    print_optimization_results, print_manual_results
)
from .geometry import (
    calculate_arrangement_area, arrangement_fits_in_pallet, ratio_score
)
from .visualization import show_2d_layout, show_arrangement_comparison

__all__ = [
    'get_user_input',
    'print_arrangement', 'print_program_header', 'print_box_info',
    'print_optimization_results', 'print_manual_results',
    'calculate_arrangement_area', 'arrangement_fits_in_pallet', 'ratio_score',
    'show_2d_layout', 'show_arrangement_comparison'
]
