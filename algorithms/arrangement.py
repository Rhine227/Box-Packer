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
    
    This function is typically used when the standard pallet size is insufficient.
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        pallet: Custom pallet with specific dimensions
        
    Returns:
        Best arrangement found, or None if no arrangement fits
    """
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
    
    return best_arrangement


def try_flexible_arrangement(box: Box, box_count: int, pallet: Pallet, max_grid_size: tuple = (8, 8)) -> Optional[List[List[str]]]:
    """
    Try to find an arrangement using a more flexible algorithm that allows mixed orientations.
    
    This algorithm uses a different approach:
    1. Tries different grid sizes that could potentially fit
    2. For each grid size, uses a placement algorithm that tries to fit boxes optimally
    3. Allows mixed orientations and empty spaces for better efficiency
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        pallet: Pallet constraints
        max_grid_size: Maximum grid size to try (rows, columns)
        
    Returns:
        2D list representing the arrangement, or None if impossible
    """
    best_arrangement = None
    best_efficiency = 0.0
    
    print(f"    Trying flexible algorithm with max grid size {max_grid_size}")
    
    # Try different grid sizes - start with reasonable sizes
    for rows in range(1, min(max_grid_size[0] + 1, 8)):
        for columns in range(1, min(max_grid_size[1] + 1, 8)):
            if rows * columns < box_count:
                continue  # Grid too small
                
            print(f"    Trying grid: {rows}x{columns}")
            
            # Try to place boxes in this grid size
            arrangement = try_flexible_placement(box, box_count, pallet, rows, columns)
            
            if arrangement is not None:
                # Calculate efficiency (how well we use the pallet space)
                arrangement_area = calculate_arrangement_area(arrangement, box)
                efficiency = (box_count * box.area) / arrangement_area if arrangement_area > 0 else 0
                
                print(f"    Grid {rows}x{columns}: SUCCESS, efficiency: {efficiency:.3f}")
                
                if efficiency > best_efficiency:
                    best_arrangement = arrangement
                    best_efficiency = efficiency
            else:
                print(f"    Grid {rows}x{columns}: FAILED")
    
    return best_arrangement


def try_flexible_placement(box: Box, box_count: int, pallet: Pallet, rows: int, columns: int) -> Optional[List[List[str]]]:
    """
    Try to place boxes in a grid using flexible placement strategy.
    
    This uses a simplified approach that tries common patterns instead of 
    exhaustive permutation search.
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        pallet: Pallet constraints
        rows: Number of rows in grid
        columns: Number of columns in grid
        
    Returns:
        2D list representing the arrangement, or None if impossible
    """
    # Initialize empty grid
    grid = [['O' for _ in range(columns)] for _ in range(rows)]
    
    # Try some common placement patterns
    patterns_to_try = [
        "fill_normal_first",    # Fill with normal orientation first
        "fill_rotated_first",   # Fill with rotated orientation first
        "mixed_columns",        # Alternate column types
        "mixed_by_space"        # Choose orientation based on available space
    ]
    
    for pattern in patterns_to_try:
        test_grid = [['O' for _ in range(columns)] for _ in range(rows)]
        boxes_placed = 0
        
        if pattern == "fill_normal_first":
            # Try to place normal boxes first, then rotated
            boxes_placed = _place_with_priority(test_grid, box, box_count, 'N', 'R', pallet)
        elif pattern == "fill_rotated_first":
            # Try to place rotated boxes first, then normal
            boxes_placed = _place_with_priority(test_grid, box, box_count, 'R', 'N', pallet)
        elif pattern == "mixed_columns":
            # Alternate between normal and rotated columns
            boxes_placed = _place_mixed_columns(test_grid, box, box_count, pallet)
        elif pattern == "mixed_by_space":
            # Choose orientation based on space efficiency
            boxes_placed = _place_by_space_efficiency(test_grid, box, box_count, pallet)
        
        # Check if this pattern worked
        if boxes_placed >= box_count and arrangement_fits_in_pallet(test_grid, box, pallet):
            return test_grid
    
    return None


def _place_with_priority(grid: List[List[str]], box: Box, box_count: int, 
                        first_orientation: str, second_orientation: str, pallet: Pallet) -> int:
    """Place boxes with priority to one orientation."""
    boxes_placed = 0
    rows, columns = len(grid), len(grid[0])
    
    # First pass: try primary orientation
    for col in range(columns):
        for row in range(rows):
            if boxes_placed >= box_count:
                break
            if grid[row][col] == 'O':
                # Try placing with primary orientation
                test_grid = [row[:] for row in grid]
                test_grid[row][col] = first_orientation
                if arrangement_fits_in_pallet(test_grid, box, pallet):
                    grid[row][col] = first_orientation
                    boxes_placed += 1
    
    # Second pass: try secondary orientation for remaining spaces
    for col in range(columns):
        for row in range(rows):
            if boxes_placed >= box_count:
                break
            if grid[row][col] == 'O':
                # Try placing with secondary orientation
                test_grid = [row[:] for row in grid]
                test_grid[row][col] = second_orientation
                if arrangement_fits_in_pallet(test_grid, box, pallet):
                    grid[row][col] = second_orientation
                    boxes_placed += 1
    
    return boxes_placed


def _place_mixed_columns(grid: List[List[str]], box: Box, box_count: int, pallet: Pallet) -> int:
    """Place boxes alternating column orientations."""
    boxes_placed = 0
    rows, columns = len(grid), len(grid[0])
    
    for col in range(columns):
        # Alternate between normal and rotated for each column
        orientation = 'N' if col % 2 == 0 else 'R'
        
        for row in range(rows):
            if boxes_placed >= box_count:
                break
                
            test_grid = [row[:] for row in grid]
            test_grid[row][col] = orientation
            if arrangement_fits_in_pallet(test_grid, box, pallet):
                grid[row][col] = orientation
                boxes_placed += 1
            else:
                break  # If one box doesn't fit, rest of column won't either
    
    return boxes_placed


def _place_by_space_efficiency(grid: List[List[str]], box: Box, box_count: int, pallet: Pallet) -> int:
    """Place boxes choosing orientation based on space efficiency."""
    boxes_placed = 0
    rows, columns = len(grid), len(grid[0])
    
    for col in range(columns):
        # Calculate remaining width for this column
        remaining_width = pallet.width - sum(_get_column_width_for_test(grid, c, box) for c in range(col))
        
        # Choose orientation based on which fits better in remaining width
        if remaining_width >= max(box.width, box.length):
            # Both orientations could fit, choose based on height efficiency
            orientation = 'R' if box.width < box.length else 'N'
        elif remaining_width >= box.width:
            orientation = 'N'
        elif remaining_width >= box.length:
            orientation = 'R'
        else:
            continue  # No room for this column
        
        for row in range(rows):
            if boxes_placed >= box_count:
                break
                
            test_grid = [row[:] for row in grid]
            test_grid[row][col] = orientation
            if arrangement_fits_in_pallet(test_grid, box, pallet):
                grid[row][col] = orientation
                boxes_placed += 1
            else:
                break  # If one box doesn't fit, rest of column won't either
    
    return boxes_placed


def _get_column_width_for_test(grid: List[List[str]], col: int, box: Box) -> float:
    """Get the width required for a specific column (for testing)."""
    max_width = 0.0
    for row in range(len(grid)):
        cell = grid[row][col]
        if cell == 'N':
            max_width = max(max_width, box.width)
        elif cell == 'R':
            max_width = max(max_width, box.length)
    return max_width


def try_smart_patterns(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """
    Try specific smart patterns that are known to work well for box packing.
    
    This function implements patterns like:
    - Mixed orientation columns (some N, some R)
    - Rectangular blocks of same orientation
    - Optimal space filling patterns
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        pallet: Pallet constraints
        
    Returns:
        2D list representing the arrangement, or None if no pattern works
    """
    patterns = [
        try_perimeter_fill_pattern,     # NEW: Prioritize perimeter filling
        try_optimal_alternating_pattern,
        _try_mixed_column_pattern,
        _try_block_pattern,
        _try_optimized_fill_pattern
    ]
    
    for pattern_func in patterns:
        result = pattern_func(box, box_count, pallet)
        if result is not None:
            print(f"    Smart pattern found: {pattern_func.__name__}")
            return result
    
    return None


def _try_mixed_column_pattern(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """Try a pattern with mixed orientation columns."""
    # Try patterns like: R-N-N-R-R (your suggested pattern)
    column_patterns = [
        ['R', 'N', 'N', 'R', 'R'],  # Your exact suggestion
        ['R', 'N', 'N', 'R'],       # 4 columns
        ['R', 'N', 'R'],            # 3 columns
        ['N', 'R', 'N', 'R'],       # Alternating
        ['R', 'R', 'N', 'N'],       # Grouped
    ]
    
    for col_pattern in column_patterns:
        # Try different row counts
        for max_rows in range(5, 9):  # Try 5-8 rows
            grid = [['O' for _ in range(len(col_pattern))] for _ in range(max_rows)]
            boxes_placed = 0
            
            # Fill the grid according to the column pattern
            for col, orientation in enumerate(col_pattern):
                # Calculate how many boxes we can fit in this column
                if orientation == 'N':
                    boxes_per_col = int(pallet.length // box.length)
                else:  # 'R'
                    boxes_per_col = int(pallet.length // box.width)
                
                # Place boxes in this column
                boxes_to_place = min(boxes_per_col, max_rows, box_count - boxes_placed)
                
                for row in range(boxes_to_place):
                    grid[row][col] = orientation
                    boxes_placed += 1
                    
                    if boxes_placed >= box_count:
                        break
                
                if boxes_placed >= box_count:
                    break
            
            # Check if this arrangement fits and has enough boxes
            if boxes_placed >= box_count and arrangement_fits_in_pallet(grid, box, pallet):
                return grid
    
    return None


def _try_block_pattern(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """Try patterns with rectangular blocks of same orientation."""
    # Try different block arrangements
    # Block pattern: create blocks of N and R orientations
    
    for n_block_rows in range(1, 6):
        for n_block_cols in range(1, 4):
            for r_block_rows in range(1, 6):
                for r_block_cols in range(1, 4):
                    
                    total_cols = n_block_cols + r_block_cols
                    total_rows = max(n_block_rows, r_block_rows)
                    
                    if total_cols > 8 or total_rows > 8:  # Keep reasonable size
                        continue
                    
                    grid = [['O' for _ in range(total_cols)] for _ in range(total_rows)]
                    boxes_placed = 0
                    
                    # Fill N block
                    for row in range(min(n_block_rows, total_rows)):
                        for col in range(n_block_cols):
                            if boxes_placed < box_count:
                                grid[row][col] = 'N'
                                boxes_placed += 1
                    
                    # Fill R block
                    for row in range(min(r_block_rows, total_rows)):
                        for col in range(n_block_cols, min(total_cols, n_block_cols + r_block_cols)):
                            if boxes_placed < box_count:
                                grid[row][col] = 'R'
                                boxes_placed += 1
                    
                    # Check if this arrangement works
                    if boxes_placed >= box_count and arrangement_fits_in_pallet(grid, box, pallet):
                        return grid
    
    return None


def _try_optimized_fill_pattern(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """Try an optimized fill pattern that maximizes space usage."""
    # Calculate how many boxes of each orientation we could theoretically fit
    normal_width = box.width
    normal_height = box.length
    rotated_width = box.length
    rotated_height = box.width
    
    # Try different mixes of orientations
    for normal_ratio in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        target_normal = int(box_count * normal_ratio)
        target_rotated = box_count - target_normal
        
        # Try to arrange these in a grid
        for rows in range(4, 9):
            for cols in range(3, 8):
                if rows * cols < box_count:
                    continue
                
                grid = [['O' for _ in range(cols)] for _ in range(rows)]
                boxes_placed = 0
                normal_placed = 0
                rotated_placed = 0
                
                # Fill grid with preferred ratio
                for row in range(rows):
                    for col in range(cols):
                        if boxes_placed >= box_count:
                            break
                        
                        # Decide orientation based on targets
                        if normal_placed < target_normal and (rotated_placed >= target_rotated or 
                                                             normal_placed / max(1, normal_placed + rotated_placed) < normal_ratio):
                            grid[row][col] = 'N'
                            normal_placed += 1
                        elif rotated_placed < target_rotated:
                            grid[row][col] = 'R'
                            rotated_placed += 1
                        else:
                            break
                        
                        boxes_placed += 1
                    
                    if boxes_placed >= box_count:
                        break
                
                # Check if this arrangement works
                if boxes_placed >= box_count and arrangement_fits_in_pallet(grid, box, pallet):
                    return grid
    
    return None


def try_optimal_alternating_pattern(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """
    Try the optimal alternating R-N pattern that maximizes standard pallet usage.
    
    This implements patterns like R-N-R-N-R which are often optimal for
    rectangular boxes.
    """
    # Calculate how many boxes of each orientation fit per column
    max_r_per_column = int(pallet.length // box.width)  # Rotated: width becomes height
    max_n_per_column = int(pallet.length // box.length)  # Normal: length becomes height
    
    print(f"    Max R boxes per column: {max_r_per_column}")
    print(f"    Max N boxes per column: {max_n_per_column}")
    
    # Try many different alternating and mixed patterns
    patterns_to_try = [
        # Alternating patterns
        ['R', 'N', 'R', 'N', 'R'],     # 3R + 2N
        ['N', 'R', 'N', 'R', 'N'],     # 3N + 2R  
        ['R', 'N', 'R', 'N'],          # 2R + 2N
        ['N', 'R', 'N', 'R'],          # 2N + 2R
        ['R', 'N', 'R'],               # 2R + 1N
        ['N', 'R', 'N'],               # 2N + 1R
        ['R', 'R', 'N', 'N'],          # 2R + 2N grouped
        ['N', 'N', 'R', 'R'],          # 2N + 2R grouped
        
        # More complex patterns
        ['R', 'R', 'N', 'R'],          # 3R + 1N mixed
        ['N', 'R', 'R', 'N'],          # 2R + 2N mixed
        ['R', 'N', 'N', 'R'],          # 2R + 2N mixed
        ['R', 'N', 'R', 'R'],          # 3R + 1N
        ['N', 'R', 'N', 'N'],          # 3N + 1R
        
        # Wider patterns
        ['R', 'N', 'R', 'N', 'R', 'N'],   # 6 columns
        ['R', 'R', 'N', 'N', 'R', 'R'],   # 6 columns grouped
        ['N', 'R', 'N', 'R', 'N', 'R'],   # 6 columns alternating
        
        # Compact patterns
        ['R', 'R'],                    # 2R only
        ['N', 'N'],                    # 2N only
        ['R', 'N'],                    # 1R + 1N
        ['N', 'R'],                    # 1N + 1R
    ]
    
    best_arrangement = None
    best_boxes_placed = 0
    best_area_efficiency = 0
    
    for pattern in patterns_to_try:
        # Calculate if this pattern fits in width
        total_width = sum(box.length if orient == 'R' else box.width for orient in pattern)
        
        if total_width > pallet.width:
            continue  # Pattern too wide
            
        print(f"    Trying pattern {pattern}, width: {total_width:.1f}")
        
        # Calculate total boxes this pattern can hold
        total_boxes_possible = sum(max_r_per_column if orient == 'R' else max_n_per_column for orient in pattern)
        
        if total_boxes_possible < box_count:
            print(f"      Not enough capacity: {total_boxes_possible} < {box_count}")
            continue  # Not enough capacity
            
        # Create the grid
        max_rows = max(max_r_per_column, max_n_per_column)
        grid = [['O' for _ in range(len(pattern))] for _ in range(max_rows)]
        
        boxes_placed = 0
        
        # Fill each column according to pattern
        for col, orientation in enumerate(pattern):
            boxes_this_column = max_r_per_column if orientation == 'R' else max_n_per_column
            boxes_to_place = min(boxes_this_column, box_count - boxes_placed)
            
            for row in range(boxes_to_place):
                grid[row][col] = orientation
                boxes_placed += 1
                
                if boxes_placed >= box_count:
                    break
            
            if boxes_placed >= box_count:
                break
        
        # Verify this arrangement fits and has the right number of boxes
        if boxes_placed >= box_count and arrangement_fits_in_pallet(grid, box, pallet):
            # Calculate area efficiency
            arrangement_area = calculate_arrangement_area(grid, box)
            area_efficiency = (boxes_placed * box.area) / arrangement_area
            
            print(f"      SUCCESS: {boxes_placed} boxes placed, area efficiency: {area_efficiency:.3f}")
            
            # Prefer arrangements with more boxes or better area efficiency
            if (boxes_placed > best_boxes_placed or 
                (boxes_placed == best_boxes_placed and area_efficiency > best_area_efficiency)):
                best_arrangement = grid
                best_boxes_placed = boxes_placed
                best_area_efficiency = area_efficiency
                print(f"      NEW BEST: {boxes_placed} boxes, efficiency: {area_efficiency:.3f}")
        else:
            if boxes_placed >= box_count:
                print(f"      FAILED: doesn't fit in pallet")
            else:
                print(f"      FAILED: only placed {boxes_placed} boxes")
    
    return best_arrangement


def try_perimeter_fill_pattern(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """
    Try patterns that fill the perimeter first and keep empty spaces in the center.
    
    This creates more stable and practical arrangements by ensuring boxes
    are around the edges for better structural support.
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        pallet: Pallet constraints
        
    Returns:
        2D list representing the arrangement, or None if impossible
    """
    # Calculate how many boxes of each orientation fit per column
    max_r_per_column = int(pallet.length // box.width)  # Rotated
    max_n_per_column = int(pallet.length // box.length)  # Normal
    
    print(f"    Trying perimeter-fill patterns")
    print(f"    Max R boxes per column: {max_r_per_column}")
    print(f"    Max N boxes per column: {max_n_per_column}")
    
    # Try different grid sizes that could accommodate the boxes
    for total_rows in range(5, 9):  # Try 5-8 rows
        for total_cols in range(3, 7):  # Try 3-6 columns
            
            if total_rows * total_cols < box_count:
                continue  # Grid too small to possibly fit all boxes
            
            # Try different perimeter patterns
            patterns = _generate_perimeter_patterns(total_rows, total_cols, box, box_count, pallet)
            
            for pattern_grid in patterns:
                if _count_boxes_in_pattern(pattern_grid) >= box_count and arrangement_fits_in_pallet(pattern_grid, box, pallet):
                    print(f"    SUCCESS: Found perimeter pattern {total_rows}x{total_cols}")
                    return pattern_grid
    
    return None


def _generate_perimeter_patterns(rows: int, cols: int, box: Box, box_count: int, pallet: Pallet) -> List[List[List[str]]]:
    """Generate patterns that fill perimeter first."""
    patterns = []
    
    # Pattern 1: Fill outer perimeter, leave center empty
    pattern1 = [['O' for _ in range(cols)] for _ in range(rows)]
    boxes_placed = 0
    
    # Fill top and bottom rows
    for col in range(cols):
        for row in [0, rows-1]:
            if boxes_placed < box_count:
                # Choose orientation based on space efficiency
                orientation = _choose_optimal_orientation(row, col, pattern1, box, pallet)
                if orientation:
                    pattern1[row][col] = orientation
                    boxes_placed += 1
    
    # Fill left and right columns (excluding corners already filled)
    for row in range(1, rows-1):
        for col in [0, cols-1]:
            if boxes_placed < box_count:
                orientation = _choose_optimal_orientation(row, col, pattern1, box, pallet)
                if orientation:
                    pattern1[row][col] = orientation
                    boxes_placed += 1
    
    # If we still need more boxes, fill some interior positions strategically
    if boxes_placed < box_count:
        # Fill from outside inward
        for layer in range(1, min(rows//2, cols//2)):
            for row in range(layer, rows-layer):
                for col in range(layer, cols-layer):
                    if (row == layer or row == rows-layer-1 or 
                        col == layer or col == cols-layer-1):
                        if pattern1[row][col] == 'O' and boxes_placed < box_count:
                            orientation = _choose_optimal_orientation(row, col, pattern1, box, pallet)
                            if orientation:
                                pattern1[row][col] = orientation
                                boxes_placed += 1
    
    if boxes_placed >= box_count:
        patterns.append(pattern1)
    
    # Pattern 2: Corner emphasis with mixed orientations
    pattern2 = [['O' for _ in range(cols)] for _ in range(rows)]
    boxes_placed = 0
    
    # Place rotated boxes at corners for stability
    corners = [(0, 0), (0, cols-1), (rows-1, 0), (rows-1, cols-1)]
    for row, col in corners:
        if boxes_placed < box_count and cols > 1 and rows > 1:
            pattern2[row][col] = 'R'
            boxes_placed += 1
    
    # Fill edges with normal orientation
    for row in range(rows):
        for col in range(cols):
            if (row == 0 or row == rows-1 or col == 0 or col == cols-1) and pattern2[row][col] == 'O':
                if boxes_placed < box_count:
                    pattern2[row][col] = 'N'
                    boxes_placed += 1
    
    # Fill interior if needed
    for row in range(1, rows-1):
        for col in range(1, cols-1):
            if pattern2[row][col] == 'O' and boxes_placed < box_count:
                orientation = _choose_optimal_orientation(row, col, pattern2, box, pallet)
                if orientation:
                    pattern2[row][col] = orientation
                    boxes_placed += 1
    
    if boxes_placed >= box_count:
        patterns.append(pattern2)
    
    return patterns


def _choose_optimal_orientation(row: int, col: int, grid: List[List[str]], box: Box, pallet: Pallet) -> Optional[str]:
    """Choose the best orientation for a box at a specific position."""
    # Try both orientations and see which fits better
    for orientation in ['N', 'R']:
        test_grid = [row[:] for row in grid]
        test_grid[row][col] = orientation
        if arrangement_fits_in_pallet(test_grid, box, pallet):
            return orientation
    return None


def _count_boxes_in_pattern(pattern: List[List[str]]) -> int:
    """Count the number of boxes in a pattern."""
    return sum(row.count('N') + row.count('R') for row in pattern)
