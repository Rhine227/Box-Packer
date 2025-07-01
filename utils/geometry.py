"""
Geometric utility functions for the Box Packer application.

This module provides functions for calculating areas, ratios,
and other geometric operations.
"""

from typing import List
from models import Box, Pallet


def calculate_arrangement_area(arrangement: List[List[str]], box: Box) -> float:
    """
    Calculate the total area required for an arrangement.
    
    Args:
        arrangement: 2D grid showing box orientations ('N', 'R', 'O')
        box: Box instance with dimensions
        
    Returns:
        Total area (width × length) required for this arrangement
    """
    if not arrangement or not arrangement[0]:
        return 0.0
        
    rows = len(arrangement)
    columns = len(arrangement[0])
    
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
                col_width = max(col_width, box.width)
                col_height += box.length
            elif cell == 'R':
                # Rotated orientation: box_l is left-right, box_w is up-down
                col_width = max(col_width, box.length)
                col_height += box.width
            # 'O' means empty space, no contribution to dimensions
        
        column_widths.append(col_width)
        column_heights.append(col_height)
    
    # Total width is sum of all column widths (side by side)
    total_width = sum(column_widths)
    # Total height is the maximum column height (tallest column determines overall height)
    total_height = max(column_heights) if column_heights else 0
    
    return total_width * total_height


def arrangement_fits_in_pallet(arrangement: List[List[str]], box: Box, pallet: Pallet) -> bool:
    """
    Check if the arrangement fits within the specified pallet dimensions.
    
    Args:
        arrangement: 2D grid of box orientations
        box: Box instance with dimensions
        pallet: Pallet instance with constraints
        
    Returns:
        True if arrangement fits within pallet dimensions, False otherwise
    """
    if not arrangement or not arrangement[0]:
        return True
        
    rows = len(arrangement)
    columns = len(arrangement[0])

    column_widths = []
    column_heights = []
    
    for c in range(columns):
        col_width = 0.0
        col_height = 0.0
        for r in range(rows):
            cell = arrangement[r][c]
            if cell == 'N':
                # Normal orientation
                col_width = max(col_width, box.width)
                col_height += box.length
            elif cell == 'R':
                # Rotated orientation
                col_width = max(col_width, box.length)
                col_height += box.width
        column_widths.append(col_width)
        column_heights.append(col_height)
    
    # Calculate total dimensions
    total_width = sum(column_widths)
    total_height = max(column_heights) if column_heights else 0
    
    return total_width <= pallet.width and total_height <= pallet.length


def ratio_score(rows: int, columns: int) -> float:
    """
    Calculate how close an arrangement is to the target 6:5 ratio.
    
    Args:
        rows: Number of rows in the arrangement
        columns: Number of columns in the arrangement
        
    Returns:
        Score indicating deviation from target ratio (lower is better)
    """
    from config import TARGET_RATIO
    
    if columns == 0:
        return float('inf')
    
    actual_ratio = rows / columns
    return abs(actual_ratio - TARGET_RATIO)
