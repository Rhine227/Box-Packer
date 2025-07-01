"""
Optimization algorithms for the Box Packer application.

This module contains algorithms for finding optimal arrangements
and automatically determining the best number of boxes per layer.
"""

from typing import Tuple, List
from models import Box, Pallet
from .arrangement import generate_candidates, try_arrangement, find_best_arrangement_with_custom_pallet
from .scaling import find_best_arrangement_with_scaling
from utils.geometry import calculate_arrangement_area, ratio_score
from config import PALLET_WIDTH, PALLET_LENGTH


def find_best_arrangement(box: Box, box_count: int) -> Tuple[List[List[str]], int, int, Pallet]:
    """
    Find the best arrangement for a specific number of boxes.
    
    This is the main function for finding arrangements. It:
    1. Tries different arrangements on the standard pallet
    2. If nothing fits, automatically scales up the pallet size
    3. Provides detailed debugging information about the process
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        
    Returns:
        Tuple containing:
        - arrangement: 2D grid of box orientations
        - rows: Number of rows in arrangement
        - columns: Number of columns in arrangement
        - pallet: Pallet instance used
        
    Note: May return scaled pallet if standard size insufficient
    """
    from utils.display import print_box_info, print_program_header
    
    print_box_info(box, box_count)
    print_program_header()
    
    candidates = generate_candidates(box_count)
    print(f"Trying {len(candidates)} different arrangements...")
    
    best_arrangement = None
    best_area = float('inf')
    best_score = float('inf')
    best_rows = 0
    best_columns = 0
    
    standard_pallet = Pallet()
    
    for rows, columns in candidates:
        arrangement = try_arrangement(rows, columns, box, box_count, standard_pallet)
        if arrangement is None:
            print(f"  Failed: {rows} rows x {columns} columns")
            continue
            
        area = calculate_arrangement_area(arrangement, box)
        score = ratio_score(rows, columns)
        
        print(f"  Success: {rows} rows x {columns} columns, area: {area}")
        
        # Prioritize arrangements with smaller area first, then better ratio
        if area < best_area or (abs(area - best_area) < 1e-6 and score < best_score):
            best_arrangement = arrangement
            best_area = area
            best_score = score
            best_rows = rows
            best_columns = columns

    # If no arrangement worked on standard pallet, try scaling
    if best_arrangement is None:
        # Provide helpful error analysis
        min_area_needed = box.area * box_count
        pallet_area_available = standard_pallet.area
        
        print(f"\\nError Analysis:")
        print(f"Minimum area needed for all boxes: {min_area_needed:.2f}")
        print(f"Available pallet area: {pallet_area_available:.2f}")
        
        if min_area_needed > pallet_area_available:
            print("The total area of all boxes exceeds the pallet area.")
        else:
            print("The boxes don't fit due to dimensional constraints.")
            
        print(f"\\nTrying to find a suitable pallet size...")
        
        try:
            return find_best_arrangement_with_scaling(box, box_count)
        except ValueError as e:
            print(f"\\nCould not find any suitable arrangement: {e}")
            print("\\nSuggestions:")
            print("1. Reduce the number of boxes per layer")
            print(f"2. Use smaller box dimensions (currently {box.width} x {box.length})")
            print("3. Consider using multiple layers or multiple pallets")
            
            # Calculate theoretical maximum for user guidance
            max_boxes_by_area = int(pallet_area_available / box.area)
            print(f"\\nTheoretical maximum boxes by area: {max_boxes_by_area}")
            raise

    return best_arrangement, best_rows, best_columns, standard_pallet


def auto_optimize_box_count(box: Box) -> Tuple[List[List[str]], int, int, int, Pallet]:
    """
    Automatically find the optimal number of boxes per layer.
    
    This advanced feature tests different box counts to find the arrangement that
    maximizes the number of boxes while staying within the original pallet size.
    No scaling is allowed during auto-optimization to ensure compliance with
    standard pallet dimensions.
    
    Args:
        box: Box instance with dimensions
        
    Returns:
        Tuple containing:
        - arrangement: Optimal 2D grid of box orientations
        - rows: Number of rows in optimal arrangement
        - columns: Number of columns in optimal arrangement
        - optimal_box_count: Best number of boxes per layer
        - final_pallet: Pallet instance used (always standard size)
    """
    print("Auto-optimizing number of boxes per layer...")
    
    # Calculate reasonable search range
    single_box_area = box.area
    original_pallet_area = PALLET_WIDTH * PALLET_LENGTH
    theoretical_max = int(original_pallet_area / single_box_area)
    
    print(f"Theoretical maximum boxes by area: {theoretical_max}")
    
    # Initialize tracking variables
    best_arrangement = None
    best_rows = 0
    best_columns = 0
    best_count = 0
    best_pallet = Pallet()
    best_efficiency = 0.0  # boxes per unit area of pallet
    
    # Define search range (start conservative, don't go too high)
    min_boxes = max(1, theoretical_max // 4)  # Start from 25% of theoretical max
    max_boxes = min(theoretical_max * 2, 100)  # Don't go too crazy with box count
    
    print(f"Testing box counts from {min_boxes} to {max_boxes}...")
    
    for box_count in range(min_boxes, max_boxes + 1):
        try:
            # Only try with original pallet - no scaling allowed during auto-optimization
            arrangement = find_best_arrangement_with_custom_pallet(box, box_count, Pallet())
            
            if arrangement is not None:
                # Found arrangement with original pallet
                rows = len(arrangement)
                columns = len(arrangement[0]) if rows > 0 else 0
                efficiency = box_count / (PALLET_WIDTH * PALLET_LENGTH)
                
                print(f"  {box_count} boxes: SUCCESS with original pallet ({rows}x{columns}), efficiency: {efficiency:.6f}")
                
                if efficiency > best_efficiency:
                    best_arrangement = arrangement
                    best_rows = rows
                    best_columns = columns
                    best_count = box_count
                    best_pallet = Pallet()
                    best_efficiency = efficiency
            else:
                print(f"  {box_count} boxes: FAILED - doesn't fit on original pallet")
        except Exception as e:
            print(f"  {box_count} boxes: ERROR - {e}")
            continue
    
    if best_arrangement is None:
        raise ValueError("Could not find any viable arrangement during auto-optimization")
    
    print(f"\\nOptimal solution: {best_count} boxes per layer")
    print(f"Arrangement: {best_rows} rows x {best_columns} columns")
    print(f"Efficiency: {best_efficiency:.6f} boxes per unit area")
    
    return best_arrangement, best_rows, best_columns, best_count, best_pallet
