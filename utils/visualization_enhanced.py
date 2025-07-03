"""
Enhanced visualization utilities for mixed arrangement patterns.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List
from models import Box, Pallet


def show_2d_layout_enhanced(arrangement: List[List[str]], box: Box, pallet: Pallet):
    """
    Display a 2D graphical representation with proper positioning for mixed arrangements.
    
    This enhanced version correctly calculates positions for mixed orientation patterns
    by determining the actual cumulative positions rather than assuming uniform grids.
    """
    if not arrangement or not arrangement[0]:
        print("No arrangement to display")
        return
    
    # First, trim unnecessary perimeter O's
    trimmed_arrangement = trim_perimeter_gaps(arrangement)
    
    if not trimmed_arrangement or not trimmed_arrangement[0]:
        print("No valid arrangement after trimming")
        return
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Set dark blue background
    fig.patch.set_facecolor('#1e3a5f')
    ax.set_facecolor('#1e3a5f')
    
    # Draw pallet as orange rectangle
    pallet_rect = patches.Rectangle(
        (0, 0), pallet.width, pallet.length,
        linewidth=3, edgecolor='orange', facecolor='orange', alpha=0.3
    )
    ax.add_patch(pallet_rect)
    
    # Calculate proper positions for mixed arrangements
    rows = len(trimmed_arrangement)
    cols = len(trimmed_arrangement[0])
    
    # Calculate column positions (x-coordinates)
    col_positions = [0]
    for c in range(cols):
        # Find the maximum width needed for this column
        max_width = 0
        for r in range(rows):
            if trimmed_arrangement[r][c] == 'N':
                max_width = max(max_width, box.width)
            elif trimmed_arrangement[r][c] == 'R':
                max_width = max(max_width, box.length)
        if max_width > 0:  # Only add width if column has boxes
            col_positions.append(col_positions[-1] + max_width)
        else:
            col_positions.append(col_positions[-1])  # Empty column, no width
    
    # Calculate row positions (y-coordinates)
    row_positions = [0]
    for r in range(rows):
        # Find the maximum height needed for this row
        max_height = 0
        for c in range(cols):
            if trimmed_arrangement[r][c] == 'N':
                max_height = max(max_height, box.length)
            elif trimmed_arrangement[r][c] == 'R':
                max_height = max(max_height, box.width)
        if max_height > 0:  # Only add height if row has boxes
            row_positions.append(row_positions[-1] + max_height)
        else:
            row_positions.append(row_positions[-1])  # Empty row, no height
    
    # Draw boxes with proper positioning
    box_number = 1
    
    for row in range(rows):
        for col in range(cols):
            orientation = trimmed_arrangement[row][col]
            
            if orientation in ['N', 'R']:  # Skip empty spaces ('O')
                # Get position from calculated arrays
                x = col_positions[col]
                y = row_positions[row]
                
                # Calculate dimensions based on orientation
                if orientation == 'N':
                    box_width = box.width
                    box_height = box.length
                else:  # orientation == 'R'
                    box_width = box.length
                    box_height = box.width
                
                # Draw the box as grey rectangle
                box_rect = patches.Rectangle(
                    (x, y), box_width, box_height,
                    linewidth=2, edgecolor='black', facecolor='lightgrey', alpha=0.8
                )
                ax.add_patch(box_rect)
                
                # Add box number in the center
                center_x = x + box_width / 2
                center_y = y + box_height / 2
                
                ax.text(center_x, center_y, str(box_number), 
                       ha='center', va='center', fontsize=12, fontweight='bold', color='black')
                
                box_number += 1
    
    # Set axis properties
    ax.set_xlim(-2, pallet.width + 2)
    ax.set_ylim(-2, pallet.length + 2)
    ax.set_aspect('equal')
    
    # Invert y-axis so row 0 is at the top
    ax.invert_yaxis()
    
    # Add labels and title
    ax.set_xlabel('Width', fontsize=12, color='white')
    ax.set_ylabel('Length', fontsize=12, color='white')
    
    box_count = sum(1 for row in trimmed_arrangement for cell in row if cell in ['N', 'R'])
    ax.set_title(f'Box Arrangement: {box_count} boxes ({rows}×{cols} grid)', 
                fontsize=16, fontweight='bold', color='white', pad=20)
    
    # Customize tick colors
    ax.tick_params(colors='white')
    
    # Add grid for better visualization
    ax.grid(True, alpha=0.3, color='white')
    
    # Add dimension annotations
    ax.annotate(f'Pallet: {pallet.width} × {pallet.length}', 
               xy=(pallet.width/2, -1), ha='center', va='top', 
               fontsize=10, color='orange', fontweight='bold')
    
    ax.annotate(f'Box: {box.width} × {box.length}', 
               xy=(pallet.width + 1, pallet.length/2), ha='left', va='center', 
               fontsize=10, color='lightgrey', fontweight='bold', rotation=90)
    
    # Show the plot
    plt.tight_layout()
    plt.show()


def trim_perimeter_gaps(arrangement: List[List[str]]) -> List[List[str]]:
    """
    Remove unnecessary empty spaces (O) from the perimeter of the arrangement.
    
    Only keeps O's that are truly interior gaps, not padding around the edges.
    """
    if not arrangement or not arrangement[0]:
        return arrangement
    
    rows = len(arrangement)
    cols = len(arrangement[0])
    
    # Find the actual bounding box of non-empty cells
    min_row, max_row = rows, -1
    min_col, max_col = cols, -1
    
    for r in range(rows):
        for c in range(cols):
            if arrangement[r][c] in ['N', 'R']:
                min_row = min(min_row, r)
                max_row = max(max_row, r)
                min_col = min(min_col, c)
                max_col = max(max_col, c)
    
    # If no boxes found, return empty
    if max_row == -1:
        return []
    
    # Extract the trimmed region
    trimmed = []
    for r in range(min_row, max_row + 1):
        row = []
        for c in range(min_col, max_col + 1):
            row.append(arrangement[r][c])
        trimmed.append(row)
    
    return trimmed


def print_arrangement_enhanced(arrangement: List[List[str]]):
    """
    Print arrangement with perimeter gaps trimmed.
    """
    trimmed = trim_perimeter_gaps(arrangement)
    
    if not trimmed:
        print("No arrangement to display")
        return
    
    box_count = sum(1 for row in trimmed for cell in row if cell in ['N', 'R'])
    print(f"Arrangement ({len(trimmed)}×{len(trimmed[0])} grid, {box_count} boxes):")
    
    for row in trimmed:
        print(" ".join(row))
