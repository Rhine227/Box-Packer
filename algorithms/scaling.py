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

def find_best_arrangement_fine_scaling(box: Box, box_count: int) -> Tuple[List[List[str]], int, int, Pallet]:
    """
    Find the best arrangement by gradually scaling up the pallet size with fine increments.
    
    This function tries arrangements on the standard pallet first, then increases
    pallet dimensions by 1/16 inch (0.0625) increments to find the smallest possible
    pallet that can accommodate the required boxes with optimal patterns.
    
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
    from .arrangement import try_smart_patterns, find_best_arrangement_with_custom_pallet
    from utils.geometry import calculate_arrangement_area
    
    original_pallet = Pallet()
    increment = 0.0625  # 1/16 inch
    max_additional_size = 8.0  # Don't go more than 8 inches larger
    
    print(f"Starting with original pallet size: {original_pallet.width} x {original_pallet.length}")
    print(f"Using fine increments of {increment} inches...")
    
    best_arrangement = None
    best_pallet = None
    best_area = float('inf')
    best_rows = 0
    best_columns = 0
    
    # Start with standard size and incrementally increase
    width_increment = 0.0
    while width_increment <= max_additional_size:
        length_increment = 0.0
        while length_increment <= max_additional_size:
            # Create test pallet with current increments
            test_width = original_pallet.width + width_increment
            test_length = original_pallet.length + length_increment
            test_pallet = Pallet(test_width, test_length)
            
            print(f"\\nTrying pallet size: {test_pallet.width:.3f} x {test_pallet.length:.3f} (+{width_increment:.3f}, +{length_increment:.3f})")
            
            # Try smart patterns first (faster and often better)
            arrangement = try_smart_patterns(box, box_count, test_pallet)
            
            # If smart patterns don't work, try traditional method
            if arrangement is None:
                arrangement = find_best_arrangement_with_custom_pallet(box, box_count, test_pallet)
            
            if arrangement is not None:
                rows = len(arrangement)
                columns = len(arrangement[0]) if rows > 0 else 0
                area = calculate_arrangement_area(arrangement, box)
                pallet_area = test_pallet.area
                
                print(f"  SUCCESS! Found arrangement: {rows}x{columns}, area used: {area:.2f}, pallet area: {pallet_area:.2f}")
                
                # Prioritize arrangements that use pallet area most efficiently
                # (closest to actual arrangement area)
                area_efficiency = area / pallet_area
                
                # If this is better (smaller pallet area, or same area but better efficiency)
                if pallet_area < best_area or (abs(pallet_area - best_area) < 1e-6 and area_efficiency > (best_area / best_pallet.area if best_pallet else 0)):
                    best_arrangement = arrangement
                    best_pallet = test_pallet
                    best_area = pallet_area
                    best_rows = rows
                    best_columns = columns
                    
                    # If we found something on standard pallet, use it immediately
                    if width_increment == 0.0 and length_increment == 0.0:
                        print(f"  Perfect fit on standard pallet!")
                        return best_arrangement, best_rows, best_columns, best_pallet
                    
                    # If we found a close fit (within 1 inch), consider stopping
                    if width_increment <= 1.0 and length_increment <= 1.0:
                        print(f"  Good fit found, but continuing to check for better options...")
            else:
                print(f"  Failed to fit {box_count} boxes")
            
            length_increment += increment
        width_increment += increment
    
    if best_arrangement is not None:
        size_increase = (best_pallet.width - original_pallet.width, best_pallet.length - original_pallet.length)
        print(f"\\nBest solution found:")
        print(f"Pallet size: {best_pallet.width:.3f} x {best_pallet.length:.3f}")
        print(f"Size increase: +{size_increase[0]:.3f}\" width, +{size_increase[1]:.3f}\" length")
        print(f"Arrangement: {best_rows} rows x {best_columns} columns")
        
        return best_arrangement, best_rows, best_columns, best_pallet
    
    raise ValueError(f"Could not find any arrangement for {box_count} boxes even with enlarged pallet")
