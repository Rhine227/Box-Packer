"""
Box Packer Program - Optimal Pallet Arrangement Calculator

This program arranges rectangular boxes into the most efficient pattern for a layer on a wooden pallet.
The program follows these key principles:
- Wooden pallets use a 6:5 ratio (rows:columns) for optimal stability
- Height should always be >= width in the display (rows >= columns)
- Boxes are built column by column for practical packing
- Boxes can be rotated 90° for better space utilization
- Empty spaces (gaps) are allowed within columns when needed

Box Orientations:
- N: Normal orientation (box length is vertical/up-down)
- R: Rotated orientation (box length is horizontal/left-right)  
- O: Empty space (gap in column for alignment)

Author: Generated with assistance
Date: July 2025
"""

from typing import List, Tuple, Optional

# Pallet configuration constants
PALLET_WIDTH = 40    # Standard pallet width in inches
PALLET_LENGTH = 48   # Standard pallet length in inches
TARGET_RATIO = 6 / 5 # Target rows/columns ratio (length/width) for optimal stability
PALLET_RATIO = PALLET_WIDTH / PALLET_LENGTH  # 0.83 for maintaining proportions during scaling

def get_user_input() -> Tuple[float, float, Optional[int]]:
    """
    Collect user input for box dimensions and optional box count.
    Ensures width <= length (shorter dimension is width, longer is length).
    
    Returns:
        Tuple containing:
        - box_width: Width of individual box (shorter dimension)
        - box_length: Length of individual box (longer dimension)  
        - box_count: Number of boxes per layer (None for auto-optimization)
    """
    width = float(input("Enter box width: "))
    length = float(input("Enter box length: "))
    
    # Validate that width is the shorter dimension
    if width > length:
        print(f"WARNING: You entered width ({width}) > length ({length}). That's stupid!")
        print("Automatically swapping them so width is the shorter dimension.")
        width, length = length, width
        print(f"Corrected dimensions: width = {width}, length = {length}")
    
    count_input = input("Enter number of boxes per layer (or press Enter to auto-optimize): ").strip()
    count = int(count_input) if count_input else None
    return width, length, count

def generate_candidates(box_count: int) -> List[Tuple[int, int]]:
    """
    Generate possible (rows, columns) arrangements that can hold all boxes.
    
    This function creates all mathematically possible grid arrangements and then
    filters/sorts them according to the program's requirements:
    1. Prioritize arrangements where rows >= columns (height >= width)
    2. Prefer arrangements closer to the 6:5 target ratio
    
    Args:
        box_count: Total number of boxes to arrange
        
    Returns:
        List of (rows, columns) tuples, sorted by preference
    """
    candidates = []
    max_rows = box_count  # Maximum rows cannot exceed total box count
    
    # Generate all possible row/column combinations
    for rows in range(1, max_rows + 1):
        columns = (box_count + rows - 1) // rows  # Ceiling division to ensure all boxes fit
        candidates.append((rows, columns))
    
    # Sort candidates to prioritize height >= width arrangements first, then by ratio closeness
    candidates.sort(key=lambda x: (x[1] > x[0], abs(x[0]/x[1] - TARGET_RATIO)))
    
    # Filter to only include arrangements where rows >= columns (height >= width)
    valid_candidates = [(rows, cols) for rows, cols in candidates if rows >= cols]
    
    # If no valid candidates found, fall back to all candidates but still prefer height >= width
    if not valid_candidates:
        return candidates  # fallback to all candidates
    
    return valid_candidates

def pallet_area(rows: int, columns: int, box_w: float, box_l: float, arrangement: List[List[str]]) -> float:
    """
    Calculate the total pallet area occupied by a specific arrangement.
    
    This function examines each column in the arrangement and calculates:
    - Maximum width needed for each column (considering box orientations)
    - Total height needed for each column (sum of stacked boxes)
    
    Args:
        rows: Number of rows in the arrangement
        columns: Number of columns in the arrangement
        box_w: Width of individual box
        box_l: Length of individual box
        arrangement: 2D grid showing box orientations ('N', 'R', 'O')
        
    Returns:
        Total area (width × length) required for this arrangement
    """
    column_widths = []
    column_heights = []
    
    # Analyze each column separately since boxes are stacked column-wise
    for c in range(columns):
        col_width = 0.0   # Maximum width needed for this column
        col_height = 0.0  # Total height of stacked boxes in this column
        
        # Check each position in the column
        for r in range(rows):
            cell = arrangement[r][c]
            if cell == 'N':
                # Normal orientation: box_w is left-right, box_l is up-down
                col_width = max(col_width, box_w)
                col_height += box_l
            elif cell == 'R':
                # Rotated orientation: box_l is left-right, box_w is up-down
                col_width = max(col_width, box_l)
                col_height += box_w
            # 'O' means empty space, no contribution to dimensions
        
        column_widths.append(col_width)
        column_heights.append(col_height)
    
    # Total width is sum of all column widths (side by side)
    total_width = sum(column_widths)
    # Total height is the maximum column height (tallest column determines overall height)
    total_height = max(column_heights) if column_heights else 0
    
    return total_width * total_height

def fits_in_pallet(arrangement: List[List[str]], box_w: float, box_l: float, pallet_w: float = PALLET_WIDTH, pallet_l: float = PALLET_LENGTH) -> bool:
    """
    Check if the arrangement fits within the specified pallet dimensions.
    
    Args:
        arrangement: 2D grid of box orientations
        box_w: Width of individual box
        box_l: Length of individual box
        pallet_w: Pallet width (default: standard pallet width)
        pallet_l: Pallet length (default: standard pallet length)
        
    Returns:
        True if arrangement fits within pallet dimensions, False otherwise
    """
    rows = len(arrangement)
    columns = len(arrangement[0]) if rows > 0 else 0

    column_widths = []
    column_heights = []
    
    # Calculate dimensions for each column
    for c in range(columns):
        col_width = 0.0
        col_height = 0.0
        for r in range(rows):
            cell = arrangement[r][c]
            if cell == 'N':
                # Normal orientation
                col_width = max(col_width, box_w)
                col_height += box_l
            elif cell == 'R':
                # Rotated orientation
                col_width = max(col_width, box_l)
                col_height += box_w
        column_widths.append(col_width)
        column_heights.append(col_height)
    
    # Calculate total dimensions
    total_width = sum(column_widths)
    total_height = max(column_heights) if column_heights else 0

    # Check if it fits within pallet constraints
    return total_width <= pallet_w and total_height <= pallet_l

def try_arrangement(rows: int, columns: int, box_w: float, box_l: float, box_count: int, pallet_w: float = PALLET_WIDTH, pallet_l: float = PALLET_LENGTH) -> Optional[List[List[str]]]:
    """
    Attempt to arrange boxes in a specific rows × columns grid configuration.
    
    This function implements the core packing algorithm:
    1. Builds arrangement column by column (as per original requirements)
    2. For each column, tries different box orientations to fit within pallet height
    3. Uses empty spaces ('O') when needed to align boxes properly
    4. Returns arrangement if successful, None if impossible to fit
    
    Args:
        rows: Number of rows in the grid
        columns: Number of columns in the grid
        box_w: Width of individual box
        box_l: Length of individual box
        box_count: Total number of boxes to place
        pallet_w: Pallet width constraint
        pallet_l: Pallet length constraint
        
    Returns:
        2D list representing the arrangement, or None if impossible
    """
    # Initialize grid with empty spaces
    arrangement = [['O' for _ in range(columns)] for _ in range(rows)]
    boxes_placed = 0

    # Process each column separately (column-wise building)
    for c in range(columns):
        # Determine how many boxes to place in this column
        boxes_in_col = min(rows, box_count - boxes_placed)
        if boxes_in_col <= 0:
            break  # No more boxes to place

        # Helper function to calculate total height of a column arrangement
        def column_height(orientations):
            """Calculate total height for a list of box orientations"""
            h = 0.0
            for orientation in orientations:
                h += box_l if orientation == 'N' else box_w
            return h

        # Strategy 1: Try all normal orientations first
        orientations = ['N'] * boxes_in_col
        
        # Strategy 2: If that doesn't fit, try rotating boxes from bottom up
        for rotate_count in range(boxes_in_col + 1):
            test_orientations = ['N'] * (boxes_in_col - rotate_count) + ['R'] * rotate_count
            if column_height(test_orientations) <= pallet_l:
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
                    if column_height(test_orientations) <= pallet_l:
                        orientations = test_orientations + ['O'] * empty_spaces
                        boxes_in_col = reduced_boxes  # Update actual boxes placed
                        break
                else:
                    continue  # Try with even fewer boxes
                break
            else:
                # Cannot fit this column at all
                return None

        # Place the determined orientations in the grid (top to bottom)
        for r in range(rows):
            if r < len(orientations):
                arrangement[r][c] = orientations[r]
            else:
                arrangement[r][c] = 'O'  # Fill remaining spots with empty spaces

        boxes_placed += boxes_in_col

    # Validate that all boxes were placed
    if boxes_placed < box_count:
        return None  # Not all boxes could be placed

    # Final check: ensure the entire arrangement fits within pallet constraints
    if not fits_in_pallet(arrangement, box_w, box_l, pallet_w, pallet_l):
        return None

    return arrangement

def ratio_score(rows: int, columns: int) -> float:
    """
    Calculate how close the rows/columns ratio is to the target 6:5 ratio.
    
    This function helps prioritize arrangements that are closer to the ideal
    wooden pallet stability ratio of 6:5 (rows:columns).
    
    Args:
        rows: Number of rows in arrangement
        columns: Number of columns in arrangement
        
    Returns:
        Float representing deviation from target ratio (lower is better)
    """
    if columns == 0:
        return float('inf')  # Avoid division by zero
    return abs((rows / columns) - TARGET_RATIO)

def find_best_arrangement_with_scaling(box_w: float, box_l: float, box_count: int) -> Tuple[List[List[str]], int, int, float, float]:
    """
    Find the best arrangement by gradually scaling up the pallet size.
    
    When boxes cannot fit in the standard 48x40 pallet, this function
    incrementally increases the pallet size while maintaining the original
    proportions until a valid arrangement is found.
    
    Args:
        box_w: Width of individual box
        box_l: Length of individual box  
        box_count: Number of boxes to arrange
        
    Returns:
        Tuple containing:
        - arrangement: 2D grid of box orientations
        - rows: Number of rows in final arrangement
        - columns: Number of columns in final arrangement  
        - final_pallet_width: Width of scaled pallet
        - final_pallet_length: Length of scaled pallet
        
    Raises:
        ValueError: If boxes cannot fit even at maximum scale factor
    """
    scale_factor = 1.0          # Start with original size
    max_scale_factor = 5.0      # Don't scale beyond 5x the original size
    scale_increment = 0.1       # Increase by 10% each iteration
    
    original_width = PALLET_WIDTH
    original_length = PALLET_LENGTH
    
    print(f"Starting with original pallet size: {original_width} x {original_length}")
    
    # Try increasingly larger pallet sizes
    while scale_factor <= max_scale_factor:
        # Calculate new pallet dimensions maintaining the original ratio
        current_width = original_width * scale_factor
        current_length = original_length * scale_factor
        
        print(f"\nTrying pallet size: {current_width:.1f} x {current_length:.1f} (scale: {scale_factor:.1f}x)")
        
        # Try to find arrangement with current pallet size
        arrangement = find_best_arrangement_with_custom_pallet(box_w, box_l, box_count, current_width, current_length)
        
        if arrangement is not None:
            rows = len(arrangement)
            columns = len(arrangement[0]) if rows > 0 else 0
            # Ensure height >= width (rows >= columns) as per requirements
            if rows >= columns:
                print(f"SUCCESS! Found arrangement with pallet size: {current_width:.1f} x {current_length:.1f}")
                return arrangement, rows, columns, current_width, current_length
            else:
                print(f"  Arrangement found but rejected: {rows} rows x {columns} columns (width > height)")
                arrangement = None
        
        scale_factor += scale_increment
    
    # If we get here, even the largest pallet couldn't fit the boxes
    raise ValueError(f"Cannot fit boxes even with pallet scaled up to {max_scale_factor}x the original size.")

def find_best_arrangement_with_custom_pallet(box_w: float, box_l: float, box_count: int, pallet_w: float, pallet_l: float) -> Optional[List[List[str]]]:
    """
    Find the best arrangement for a specific custom pallet size.
    
    This function tries different arrangements on a pallet with custom dimensions,
    typically used when the standard pallet size is insufficient.
    
    Args:
        box_w: Width of individual box
        box_l: Length of individual box
        box_count: Number of boxes to arrange
        pallet_w: Custom pallet width
        pallet_l: Custom pallet length
        
    Returns:
        Best arrangement found, or None if no arrangement fits
    """
    candidates = generate_candidates(box_count)
    best_arrangement = None
    best_score = float('inf')     # Lower ratio score is better
    best_area = float('inf')      # Lower area usage is better
    
    # Try each candidate arrangement
    for rows, columns in candidates:
        arrangement = try_arrangement(rows, columns, box_w, box_l, box_count, pallet_w, pallet_l)
        if arrangement is None:
            continue  # This arrangement didn't work
            
        # Calculate metrics for this arrangement
        area = pallet_area(rows, columns, box_w, box_l, arrangement)
        score = ratio_score(rows, columns)
        
        # Prioritize arrangements with smaller area first, then better ratio
        if area < best_area or (abs(area - best_area) < 1e-6 and score < best_score):
            best_arrangement = arrangement
            best_area = area
            best_score = score

    return best_arrangement

def find_best_arrangement(box_w: float, box_l: float, box_count: int) -> Tuple[List[List[str]], int, int]:
    """
    Find the best arrangement using the standard pallet size.
    
    This is the main arrangement function that:
    1. Tries different arrangements on the standard 48x40 pallet
    2. If nothing fits, automatically scales up the pallet size
    3. Provides detailed debugging information about the process
    
    Args:
        box_w: Width of individual box
        box_l: Length of individual box
        box_count: Number of boxes to arrange
        
    Returns:
        Tuple containing:
        - arrangement: 2D grid of box orientations
        - rows: Number of rows in arrangement
        - columns: Number of columns in arrangement
        
    Note: May return 5 values if scaling was needed (includes pallet dimensions)
    """
    candidates = generate_candidates(box_count)
    best_arrangement = None
    best_score = float('inf')
    best_area = float('inf')
    best_rows = 0
    best_columns = 0
    
    # Provide user feedback about the process
    print(f"Box dimensions: {box_w} x {box_l}")
    print(f"Pallet dimensions: {PALLET_WIDTH} x {PALLET_LENGTH}")
    print(f"Number of boxes: {box_count}")
    print(f"Trying {len(candidates)} different arrangements...")

    # Try each candidate arrangement on standard pallet
    for rows, columns in candidates:
        arrangement = try_arrangement(rows, columns, box_w, box_l, box_count)
        if arrangement is None:
            print(f"  Failed: {rows} rows x {columns} columns")
            continue
            
        area = pallet_area(rows, columns, box_w, box_l, arrangement)
        score = ratio_score(rows, columns)
        print(f"  Success: {rows} rows x {columns} columns, area: {area:.2f}")
        
        # Select best arrangement based on area efficiency and ratio
        if area < best_area or (abs(area - best_area) < 1e-6 and score < best_score):
            best_arrangement = arrangement
            best_area = area
            best_score = score
            best_rows = rows
            best_columns = columns

    # If no arrangement worked on standard pallet, try scaling
    if best_arrangement is None:
        # Provide helpful error analysis
        min_area_needed = box_w * box_l * box_count
        pallet_area_available = PALLET_WIDTH * PALLET_LENGTH
        
        print(f"\nError Analysis:")
        print(f"Minimum area needed for all boxes: {min_area_needed:.2f}")
        print(f"Available pallet area: {pallet_area_available:.2f}")
        
        if min_area_needed > pallet_area_available:
            print("The total area of all boxes exceeds the pallet area.")
        else:
            print("The boxes don't fit due to dimensional constraints.")
            
        print(f"\nTrying to find a suitable pallet size...")
        # Try with scaling pallet size
        try:
            return find_best_arrangement_with_scaling(box_w, box_l, box_count)
        except ValueError as scale_error:
            print(f"\nSuggestions:")
            print(f"1. Reduce the number of boxes (currently {box_count})")
            print(f"2. Use smaller box dimensions (currently {box_w} x {box_l})")
            print(f"3. Consider a larger pallet size")
            
            # Try to suggest a maximum number of boxes that might fit
            max_boxes_by_area = int(pallet_area_available / (box_w * box_l))
            print(f"4. Maximum boxes by area calculation: {max_boxes_by_area}")
            
            raise ValueError("Cannot fit boxes within pallet with given dimensions.")

    return best_arrangement, best_rows, best_columns

def print_arrangement(arrangement: List[List[str]]):
    """
    Display the final arrangement pattern in a readable format.
    
    Prints each row of the arrangement grid, showing:
    - N: Normal orientation boxes
    - R: Rotated orientation boxes  
    - O: Empty spaces
    
    Args:
        arrangement: 2D grid of box orientations to display
    """
    for row in arrangement:
        print(' '.join(row))

def auto_optimize_box_count(box_w: float, box_l: float) -> Tuple[List[List[str]], int, int, int, float, float]:
    """
    Automatically determine the optimal number of boxes per layer for maximum efficiency.
    
    This advanced feature tests different box counts to find the arrangement that
    maximizes the number of boxes while maintaining the height >= width requirement
    and preferring arrangements that fit within the original pallet size.
    
    Args:
        box_w: Width of individual box
        box_l: Length of individual box
        
    Returns:
        Tuple containing:
        - arrangement: Optimal 2D grid of box orientations
        - rows: Number of rows in optimal arrangement
        - columns: Number of columns in optimal arrangement
        - optimal_box_count: Best number of boxes per layer
        - final_pallet_width: Width of pallet used
        - final_pallet_length: Length of pallet used
        
    Raises:
        ValueError: If no viable arrangement can be found
    """
    print("Auto-optimizing number of boxes per layer...")
    
    # Calculate theoretical limits
    original_pallet_area = PALLET_WIDTH * PALLET_LENGTH
    single_box_area = box_w * box_l
    theoretical_max = int(original_pallet_area / single_box_area)
    
    print(f"Theoretical maximum boxes by area: {theoretical_max}")
    
    # Track the best solution found
    best_arrangement = None
    best_rows = 0
    best_columns = 0
    best_count = 0
    best_pallet_width = PALLET_WIDTH
    best_pallet_length = PALLET_LENGTH
    best_efficiency = 0.0  # boxes per unit area of pallet
    
    # Define search range (start conservative, don't go too high)
    min_boxes = max(1, theoretical_max // 4)  # Start from 25% of theoretical max
    max_boxes = min(theoretical_max * 2, 100)  # Don't go too crazy with box count
    
    print(f"Testing box counts from {min_boxes} to {max_boxes}...")
    
    # Test each possible box count
    for box_count in range(min_boxes, max_boxes + 1):
        try:
            # First try with original pallet size (preferred)
            arrangement = find_best_arrangement_with_custom_pallet(box_w, box_l, box_count, PALLET_WIDTH, PALLET_LENGTH)
            
            if arrangement is not None:
                # Found arrangement with original pallet - this is preferred
                rows = len(arrangement)
                columns = len(arrangement[0]) if rows > 0 else 0
                efficiency = box_count / (PALLET_WIDTH * PALLET_LENGTH)
                
                print(f"  {box_count} boxes: SUCCESS with original pallet ({rows}x{columns}), efficiency: {efficiency:.6f}")
                
                if efficiency > best_efficiency:
                    best_arrangement = arrangement
                    best_rows = rows
                    best_columns = columns
                    best_count = box_count
                    best_pallet_width = PALLET_WIDTH
                    best_pallet_length = PALLET_LENGTH
                    best_efficiency = efficiency
            else:
                # Try with scaling if original pallet doesn't work
                try:
                    arrangement, rows, columns, pallet_w, pallet_l = find_best_arrangement_with_scaling(box_w, box_l, box_count)
                    efficiency = box_count / (pallet_w * pallet_l)
                    scale_factor = pallet_w / PALLET_WIDTH
                    
                    print(f"  {box_count} boxes: SUCCESS with {scale_factor:.1f}x pallet ({rows}x{columns}), efficiency: {efficiency:.6f}")
                    
                    # Prefer arrangements that fit in original pallet, but consider scaled ones if efficiency is much better
                    efficiency_threshold = best_efficiency * 1.2  # Need 20% better efficiency to justify scaling
                    if efficiency > efficiency_threshold or best_arrangement is None:
                        best_arrangement = arrangement
                        best_rows = rows
                        best_columns = columns
                        best_count = box_count
                        best_pallet_width = pallet_w
                        best_pallet_length = pallet_l
                        best_efficiency = efficiency
                except ValueError:
                    print(f"  {box_count} boxes: FAILED even with scaling")
                    continue
        except Exception as e:
            print(f"  {box_count} boxes: ERROR - {e}")
            continue
    
    if best_arrangement is None:
        raise ValueError("Could not find any viable arrangement for auto-optimization")
    
    print(f"\nOptimal solution: {best_count} boxes per layer")
    print(f"Arrangement: {best_rows} rows x {best_columns} columns")
    print(f"Efficiency: {best_efficiency:.6f} boxes per unit area")
    
    return best_arrangement, best_rows, best_columns, best_count, best_pallet_width, best_pallet_length

def main():
    """
    Main program loop that handles user interaction and coordinates the packing process.
    
    This function provides a user-friendly interface that:
    1. Collects box dimensions and optional box count from user
    2. Either auto-optimizes the number of boxes or uses the provided count
    3. Handles both standard pallet and scaled pallet solutions
    4. Provides clear output showing the final arrangement
    5. Allows the user to retry with different inputs on errors
    
    The program continues running until the user chooses to exit.
    """
    while True:
        try:
            # Get user input for box dimensions and optional count
            box_w, box_l, box_count = get_user_input()
            
            if box_count is None:
                # Auto-optimization mode: find optimal number of boxes
                result = auto_optimize_box_count(box_w, box_l)
                arrangement, rows, columns, optimal_count, final_width, final_length = result
                
                print(f"\nOptimal arrangement: {rows} rows x {columns} columns")
                print(f"Optimal boxes per layer: {optimal_count}")
                
                # Show pallet size information
                if final_width != PALLET_WIDTH or final_length != PALLET_LENGTH:
                    print(f"Final pallet size: {final_width:.1f} x {final_length:.1f}")
                    scale_factor = final_width / PALLET_WIDTH
                    print(f"Scale factor: {scale_factor:.1f}x original size")
                else:
                    print(f"Pallet size: {PALLET_WIDTH} x {PALLET_LENGTH} (original)")
            else:
                # Manual mode: use provided box count
                result = find_best_arrangement(box_w, box_l, box_count)
                
                if len(result) == 3:
                    # Standard arrangement (fits in original pallet)
                    arrangement, rows, columns = result
                    print(f"\nBest arrangement: {rows} rows x {columns} columns")
                    print(f"Pallet size: {PALLET_WIDTH} x {PALLET_LENGTH}")
                else:
                    # Scaled arrangement (required larger pallet)
                    arrangement, rows, columns, final_width, final_length = result
                    print(f"\nBest arrangement: {rows} rows x {columns} columns")
                    print(f"WARNING: Your requested {box_count} boxes required a larger pallet!")
                    print(f"Final pallet size: {final_width:.1f} x {final_length:.1f}")
                    scale_factor = final_width / PALLET_WIDTH
                    print(f"Scale factor: {scale_factor:.1f}x original size")
                    pallet_area_increase = (final_width * final_length) / (PALLET_WIDTH * PALLET_LENGTH)
                    print(f"Pallet area increased by {pallet_area_increase:.1f}x")
            
            # Display the final arrangement pattern
            print()
            print_arrangement(arrangement)
            
            # Return the arrangement for potential further use
            return arrangement
            
        except ValueError as e:
            # Handle errors gracefully and offer retry option
            print(f"\nError: {e}")
            retry = input("\nWould you like to try again with different inputs? (y/n): ").lower().strip()
            if retry != 'y' and retry != 'yes':
                print("Exiting program.")
                return None


# Program entry point
if __name__ == "__main__":
    main()