"""
Pallet scaling algorithms for the Box Packer application.

This module handles automatic pallet scaling when arrangements
don't fit within the standard pallet dimensions.
"""

from typing import Tuple, List
from models import Box, Pallet
from .arrangement import find_best_arrangement_with_custom_pallet
from config import PALLET_WIDTH, PALLET_LENGTH, DEFAULT_SCALE_INCREMENT, MAX_SCALE_FACTOR


def find_best_arrangement_with_scaling(box: Box, box_count: int) -> Tuple[List[List[str]], int, int, Pallet]:
    """
    Find the best arrangement by gradually scaling up the pallet size.
    
    This function starts with the standard pallet size and then 
    incrementally increases the pallet size while maintaining the original
    proportions until a valid arrangement is found.
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        
    Returns:
        Tuple containing:
        - arrangement: 2D grid of box orientations
        - rows: Number of rows in final arrangement
        - columns: Number of columns in final arrangement  
        - final_pallet: Pallet instance used for the arrangement
    """
    scale_factor = 1.0
    scale_increment = DEFAULT_SCALE_INCREMENT
    max_scale_factor = MAX_SCALE_FACTOR
    
    original_pallet = Pallet()
    
    print(f"Starting with original pallet size: {original_pallet.width} x {original_pallet.length}")
    
    # Try increasingly larger pallet sizes
    while scale_factor <= max_scale_factor:
        # Calculate new pallet dimensions maintaining the original ratio
        current_pallet = original_pallet.scale(scale_factor)
        
        print(f"\\nTrying pallet size: {current_pallet.width:.1f} x {current_pallet.length:.1f} (scale: {scale_factor:.1f}x)")
        
        # Try to find arrangement with current pallet size
        arrangement = find_best_arrangement_with_custom_pallet(box, box_count, current_pallet)
        
        if arrangement is not None:
            rows = len(arrangement)
            columns = len(arrangement[0]) if rows > 0 else 0
            # Ensure height >= width (rows >= columns) as per requirements
            if rows >= columns:
                print(f"SUCCESS! Found arrangement with pallet size: {current_pallet.width:.1f} x {current_pallet.length:.1f}")
                return arrangement, rows, columns, current_pallet
            else:
                print(f"  Arrangement found but rejected: {rows} rows x {columns} columns (width > height)")
                arrangement = None
        
        scale_factor += scale_increment
    
    # If we get here, even the largest pallet couldn't fit the boxes
    raise ValueError(f"Cannot fit boxes even with pallet scaled up to {max_scale_factor}x the original size.")
