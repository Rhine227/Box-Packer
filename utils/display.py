"""
Display utilities for the Box Packer application.

This module handles output formatting and arrangement visualization.
"""

from typing import List
from models import Box, Pallet


def print_arrangement(arrangement: List[List[str]]) -> None:
    """
    Print a visual representation of the box arrangement.
    
    Args:
        arrangement: 2D grid of box orientations ('N', 'R', 'O')
    """
    for row in arrangement:
        print(' '.join(row))


def print_program_header() -> None:
    """Print the program header and pallet information."""
    from config import PALLET_WIDTH, PALLET_LENGTH
    
    print(f"Pallet dimensions: {PALLET_WIDTH} x {PALLET_LENGTH}")


def print_box_info(box: Box, box_count: int) -> None:
    """
    Print information about the box dimensions and count.
    
    Args:
        box: Box instance
        box_count: Number of boxes to arrange
    """
    print(f"Box dimensions: {box.width} x {box.length}")
    print(f"Number of boxes: {box_count}")


def print_optimization_results(arrangement: List[List[str]], rows: int, columns: int, 
                             optimal_count: int, pallet: Pallet) -> None:
    """
    Print the results of auto-optimization.
    
    Args:
        arrangement: The optimal arrangement found
        rows: Number of rows in arrangement
        columns: Number of columns in arrangement
        optimal_count: Optimal number of boxes per layer
        pallet: Final pallet used
    """
    print(f"\nOptimal arrangement: {rows} rows x {columns} columns")
    print(f"Optimal boxes per layer: {optimal_count}")
    
    # Show pallet size information
    if not pallet.is_standard_size:
        from config import PALLET_WIDTH, PALLET_LENGTH
        print(f"Final pallet size: {pallet.width:.1f} x {pallet.length:.1f}")
        scale_factor = pallet.width / PALLET_WIDTH
        print(f"Scale factor: {scale_factor:.1f}x original size")
    else:
        print(f"Pallet size: {pallet.width} x {pallet.length} (original)")


def print_manual_results(arrangement: List[List[str]], rows: int, columns: int, 
                        pallet: Pallet, box_count: int) -> None:
    """
    Print the results of manual box count specification.
    
    Args:
        arrangement: The arrangement found
        rows: Number of rows in arrangement
        columns: Number of columns in arrangement
        pallet: Final pallet used
        box_count: User-specified box count
    """
    print(f"\nBest arrangement: {rows} rows x {columns} columns")
    
    if not pallet.is_standard_size:
        from config import PALLET_WIDTH, PALLET_LENGTH
        print(f"WARNING: Your requested {box_count} boxes required a larger pallet!")
        print(f"Final pallet size: {pallet.width:.1f} x {pallet.length:.1f}")
        scale_factor = pallet.width / PALLET_WIDTH
        print(f"Scale factor: {scale_factor:.1f}x original size")
        pallet_area_increase = pallet.area / (PALLET_WIDTH * PALLET_LENGTH)
        print(f"Pallet area increased by {pallet_area_increase:.1f}x")
    else:
        print(f"Pallet size: {pallet.width} x {pallet.length}")
