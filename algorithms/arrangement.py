"""
Core arrangement algorithms for the Box Packer application.

This module contains the fundamental algorithms for generating
box arrangements and testing their validity.
"""

from typing import List, Tuple, Optional
from models import Box, Pallet
from utils.geometry import arrangement_fits_in_pallet, ratio_score, calculate_arrangement_area
from config import TARGET_RATIO


def generate_candidates(box_count: int) -> List[Tuple[int, int]]:
    """
    Generate possible (rows, columns) arrangements that can hold all boxes.
    
    This function creates all mathematically possible grid arrangements and then
    filters/sorts them according to the program's requirements:
    1. Only arrangements where rows >= columns (height >= width requirement)
    2. Sorted by proximity to the target 6:5 ratio for optimal stability
    
    Args:
        box_count: Total number of boxes to arrange
        
    Returns:
        List of (rows, columns) tuples, sorted by preference
    """
    candidates = []
    
    # Generate all possible factor pairs
    for i in range(1, box_count + 1):
        if box_count % i == 0:
            rows = i
            columns = box_count // i
            
            # Only consider arrangements where rows >= columns (height >= width)
            if rows >= columns:
                candidates.append((rows, columns))
    
    # Sort by proximity to target ratio (6:5), then by total area efficiency
    candidates.sort(key=lambda rc: (ratio_score(rc[0], rc[1]), rc[0] * rc[1]))
    
    return candidates


def try_arrangement(rows: int, columns: int, box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """
    Attempt to create a specific grid arrangement using the column-wise building strategy.
    
    This function implements the core packing algorithm:
    1. Builds the arrangement column by column (left to right)
    2. For each column, tries to fit boxes optimally within pallet height constraint
    3. Uses rotation ('N' vs 'R') and empty spaces ('O') as needed
    4. Returns arrangement if successful, None if impossible to fit
    
    Args:
        rows: Number of rows in the grid
        columns: Number of columns in the grid
        box: Box instance with dimensions
        box_count: Total number of boxes to place
        pallet: Pallet constraints
        
    Returns:
        2D list representing the arrangement, or None if impossible
    """
    # Initialize grid with empty spaces
    arrangement = [['O' for _ in range(columns)] for _ in range(rows)]
    
    boxes_placed = 0
    
    for col in range(columns):
        # Calculate how many boxes should go in this column
        remaining_boxes = box_count - boxes_placed
        remaining_columns = columns - col
        boxes_in_col = min(rows, (remaining_boxes + remaining_columns - 1) // remaining_columns)
        
        if boxes_in_col == 0:
            continue  # No more boxes needed
        
        # Helper function to calculate total height of a column arrangement
        def column_height(orientations):
            """Calculate total height for a list of box orientations"""
            h = 0.0
            for orientation in orientations:
                h += box.length if orientation == 'N' else box.width
            return h

        # Strategy 1: Try all normal orientations first
        orientations = ['N'] * boxes_in_col
        
        # Strategy 2: If that doesn't fit, try rotating boxes from bottom up
        for rotate_count in range(boxes_in_col + 1):
            test_orientations = ['N'] * (boxes_in_col - rotate_count) + ['R'] * rotate_count
            if column_height(test_orientations) <= pallet.length:
                orientations = test_orientations
                break
        else:
            # Strategy 3: If still doesn't fit, try using fewer boxes with empty spaces
            for empty_spaces in range(1, rows - boxes_in_col + 1):
                reduced_boxes = boxes_in_col - empty_spaces
                if reduced_boxes <= 0:
                    break
                    
                # Try different rotations with fewer boxes
                for rotate_count in range(reduced_boxes + 1):
                    test_orientations = ['N'] * (reduced_boxes - rotate_count) + ['R'] * rotate_count
                    if column_height(test_orientations) <= pallet.length:
                        orientations = test_orientations + ['O'] * empty_spaces
                        boxes_in_col = reduced_boxes  # Update actual boxes placed
                        break
                else:
                    continue
                break
            else:
                # Could not fit boxes in this column even with reductions
                return None
        
        # Place the determined orientations in the column
        for i, orientation in enumerate(orientations):
            if i < rows:  # Safety check
                arrangement[i][col] = orientation
        
        boxes_placed += boxes_in_col
    
    # Verify the final arrangement fits in the pallet
    if not arrangement_fits_in_pallet(arrangement, box, pallet):
        return None
    
    return arrangement


def find_best_arrangement_with_custom_pallet(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """
    Find the best arrangement for a given box count using a custom pallet size.
    
    This function tries multiple strategies:
    1. Standard rectangular grid patterns
    2. Advanced mixed-orientation patterns
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        pallet: Custom pallet with specific dimensions
        
    Returns:
        Best arrangement found, or None if no arrangement fits
    """
    # First try standard rectangular patterns
    candidates = generate_candidates(box_count)
    
    best_arrangement = None
    best_area = float('inf')
    best_score = float('inf')
    
    for rows, columns in candidates:
        arrangement = try_arrangement(rows, columns, box, box_count, pallet)
        if arrangement is None:
            continue  # This arrangement didn't work
            
        # Calculate metrics for this arrangement
        area = calculate_arrangement_area(arrangement, box)
        score = ratio_score(rows, columns)
        
        # Prioritize arrangements with smaller area first, then better ratio
        if area < best_area or (abs(area - best_area) < 1e-6 and score < best_score):
            best_arrangement = arrangement
            best_area = area
            best_score = score
    
    # Always try advanced mixed patterns and spatial 2D placement
    from .advanced_patterns import try_mixed_pattern_arrangement
    from .spatial_2d import find_2d_spatial_arrangement
    
    # Try spatial 2D placement first (more sophisticated)
    spatial_arrangement = find_2d_spatial_arrangement(box, box_count, pallet)
    if spatial_arrangement:
        spatial_area = calculate_arrangement_area(spatial_arrangement, box)
        if best_arrangement is None or spatial_area <= best_area:
            print(f"Found spatial 2D arrangement!")
            return spatial_arrangement
    
    # Try advanced mixed patterns
    advanced_arrangement = try_mixed_pattern_arrangement(box, box_count, pallet)
    if advanced_arrangement:
        # If we found an advanced pattern, prefer it for complex arrangements
        advanced_area = calculate_arrangement_area(advanced_arrangement, box)
        if best_arrangement is None or advanced_area <= best_area:
            print(f"Found advanced mixed pattern!")
            return advanced_arrangement
    
    return best_arrangement
