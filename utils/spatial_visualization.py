"""
Spatial 2D visualization for true box placement without grid constraints.

This module visualizes boxes using their actual spatial coordinates,
showing them butted up against each other as they would be in reality.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Optional
from models import Box, Pallet
from algorithms.spatial_2d import BoxPlacement, find_2d_spatial_arrangement


def show_spatial_layout(box: Box, box_count: int, pallet: Pallet, arrangement: Optional[List[List[str]]] = None):
    """
    Display a true spatial 2D visualization where boxes are positioned using actual coordinates.
    
    Args:
        box: Box instance with dimensions
        box_count: Target number of boxes
        pallet: Pallet constraints
        arrangement: Grid arrangement to convert to spatial placement
    """
    # Convert grid arrangement to spatial placements
    if arrangement:
        placements = _convert_grid_to_spatial_placements(arrangement, box, pallet)
    else:
        # Fallback to our own spatial arrangement algorithm
        placements = create_spatial_arrangement(box, box_count, pallet)
    
    if not placements:
        print("No box placements to display.")
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
    
    # Calculate pattern boundaries
    pattern_width = _calculate_pattern_width(arrangement, box) if arrangement else 0
    pattern_length = _calculate_pattern_length(arrangement, box) if arrangement else 0
    
    # Draw pattern boundary as a dashed rectangle if pattern fits within pallet
    if pattern_width > 0 and pattern_length > 0:
        pattern_rect = patches.Rectangle(
            (0, 0), pattern_width, pattern_length,
            linewidth=2, edgecolor='yellow', facecolor='none', 
            linestyle='--', alpha=0.8
        )
        ax.add_patch(pattern_rect)
        
        # Add pattern dimension annotation
        ax.annotate(f'Pattern: {pattern_width:.1f}" × {pattern_length:.1f}"', 
                   xy=(pattern_width/2, pattern_length + 1), ha='center', va='bottom', 
                   fontsize=10, color='yellow', fontweight='bold')
    
    # Draw each box using its exact spatial coordinates
    for i, placement in enumerate(placements):
        # Draw the box as grey rectangle at exact position
        box_rect = patches.Rectangle(
            (placement.x, placement.y), placement.width, placement.length,
            linewidth=2, edgecolor='black', facecolor='lightgrey', alpha=0.8
        )
        ax.add_patch(box_rect)
        
        # Add box number in the center
        center_x = placement.x + placement.width / 2
        center_y = placement.y + placement.length / 2
        
        ax.text(center_x, center_y, str(i + 1), 
               ha='center', va='center', fontsize=12, fontweight='bold', color='black')
        
        # Add orientation indicator (small letter in corner)
        ax.text(placement.x + 2, placement.y + 2, placement.orientation, 
               ha='left', va='bottom', fontsize=8, fontweight='bold', color='darkblue')
    
    # Set axis properties
    ax.set_xlim(-2, pallet.width + 2)
    ax.set_ylim(-2, pallet.length + 2)
    ax.set_aspect('equal')
    
    # Invert y-axis so (0,0) is at top-left like traditional packing diagrams
    ax.invert_yaxis()
    
    # Add labels and title
    ax.set_xlabel('Width (inches)', fontsize=12, color='white')
    ax.set_ylabel('Length (inches)', fontsize=12, color='white')
    
    actual_count = len(placements)
    efficiency = (actual_count * box.width * box.length) / (pallet.width * pallet.length) * 100
    
    ax.set_title(f'Spatial Box Arrangement: {actual_count} boxes ({efficiency:.1f}% efficiency)', 
                fontsize=16, fontweight='bold', color='white', pad=20)
    
    # Customize tick colors
    ax.tick_params(colors='white')
    
    # Add subtle grid for reference
    ax.grid(True, alpha=0.2, color='white', linestyle='--')
    
    # Add dimension annotations
    ax.annotate(f'Pallet: {pallet.width}" × {pallet.length}"', 
               xy=(pallet.width/2, -1), ha='center', va='top', 
               fontsize=10, color='orange', fontweight='bold')
    
    ax.annotate(f'Box: {box.width}" × {box.length}"', 
               xy=(pallet.width + 1, pallet.length/2), ha='left', va='center', 
               fontsize=10, color='lightgrey', fontweight='bold', rotation=90)
    
    # Add legend for orientations
    legend_text = "Orientations: N = Normal, R = Rotated 90°"
    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes, 
           fontsize=9, color='white', va='top', ha='left',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
    
    # Show the plot
    plt.tight_layout()
    plt.show()


def create_spatial_arrangement(box: Box, box_count: int, pallet: Pallet) -> List[BoxPlacement]:
    """
    Create a spatial arrangement using true butting placement algorithms.
    
    Places boxes one by one, always pushing them as far up and left as possible.
    """
    placements = []
    
    for i in range(box_count):
        # Try both orientations for each box
        best_position = None
        best_orientation = None
        best_score = float('inf')
        
        for orientation in ['N', 'R']:
            if orientation == 'N':
                width, length = box.width, box.length
            else:
                width, length = box.length, box.width
            
            # Find the butted position for this orientation
            x, y = _find_butted_position(placements, width, length, pallet)
            
            # Check if it fits within pallet bounds
            if x + width <= pallet.width and y + length <= pallet.length:
                # Score based on how far top-left the position is (prefer top-left)
                score = y * 1000 + x  # Heavily weight y-position (top), then x-position (left)
                
                if score < best_score:
                    best_score = score
                    best_position = (x, y)
                    best_orientation = orientation
                    best_dimensions = (width, length)
        
        # Place the box in the best position found
        if best_position and best_orientation:
            x, y = best_position
            width, length = best_dimensions
            placements.append(BoxPlacement(x, y, width, length, best_orientation))
        else:
            # Can't fit any more boxes
            break
    
    return placements


def _convert_grid_to_spatial_placements(grid: List[List[str]], box: Box, pallet: Pallet) -> List[BoxPlacement]:
    """
    Convert a grid arrangement to spatial placements that respect the grid structure
    but eliminate gaps between boxes by calculating actual cumulative positions.
    """
    placements = []
    
    if not grid or not grid[0]:
        return placements
    
    rows = len(grid)
    cols = len(grid[0])
    
    # For each row, calculate the Y position by accumulating heights of previous rows
    current_y = 0.0
    
    for row in range(rows):
        # For this row, calculate X positions by accumulating widths
        current_x = 0.0
        row_height = 0.0
        
        for col in range(cols):
            orientation = grid[row][col]
            
            if orientation in ['N', 'R']:
                if orientation == 'N':
                    width, length = box.width, box.length
                else:  # orientation == 'R'
                    width, length = box.length, box.width
                
                # Place box at current position
                placements.append(BoxPlacement(current_x, current_y, width, length, orientation))
                
                # Move X position for next box in this row
                current_x += width
                
                # Track the maximum height in this row
                row_height = max(row_height, length)
            
            # For 'O' (empty), we don't advance position - just skip
        
        # Move Y position for next row
        current_y += row_height
    
    return placements


def _find_butted_position(existing_placements: List[BoxPlacement], width: float, length: float, pallet: Pallet) -> tuple[float, float]:
    """
    Find the position where a box should be placed by pushing it as far up and left as possible.
    
    Algorithm:
    1. Try to place at (0,0) first
    2. If that overlaps, find the lowest possible Y position
    3. For that Y position, find the leftmost possible X position
    """
    if not existing_placements:
        return (0.0, 0.0)
    
    # Try all possible Y positions (bottom edges of existing boxes + 0)
    possible_y = [0.0]
    for placement in existing_placements:
        possible_y.append(placement.bottom)
    
    # Sort Y positions from top to bottom
    possible_y.sort()
    
    # For each Y position, find the leftmost X where the box fits
    for y in possible_y:
        # Check if box fits vertically at this Y position
        if y + length <= pallet.length:
            # Find the leftmost X position at this Y
            x = _find_leftmost_x_at_y(existing_placements, y, width, length, pallet)
            if x is not None:
                return (x, y)
    
    # Fallback - shouldn't happen if pallet is large enough
    return (0.0, 0.0)


def _find_leftmost_x_at_y(existing_placements: List[BoxPlacement], y: float, width: float, length: float, pallet: Pallet) -> float:
    """
    Find the leftmost X position where a box can be placed at the given Y position.
    """
    # Try all possible X positions (right edges of existing boxes + 0)
    possible_x = [0.0]
    
    # Add right edges of boxes that might conflict with this Y range
    for placement in existing_placements:
        # Check if this existing box overlaps vertically with our proposed box
        if not (y + length <= placement.y or y >= placement.bottom):
            possible_x.append(placement.right)
    
    # Sort X positions from left to right
    possible_x.sort()
    
    # Try each X position until we find one that works
    for x in possible_x:
        if x + width <= pallet.width:
            # Check if placing box at (x, y) would cause any overlaps
            if not _check_overlap_at_position(existing_placements, x, y, width, length):
                return x
    
    # If no position found, return None
    return None


def _check_overlap_at_position(existing_placements: List[BoxPlacement], x: float, y: float, width: float, length: float) -> bool:
    """
    Check if placing a box at (x, y) with given dimensions would overlap with any existing boxes.
    """
    for placement in existing_placements:
        if (x < placement.right and x + width > placement.x and
            y < placement.bottom and y + length > placement.y):
            return True
    return False


def _calculate_pattern_width(grid: List[List[str]], box: Box) -> float:
    """Calculate pattern width using the bottom row method."""
    if not grid or not grid[0]:
        return 0.0
    
    bottom_row = grid[-1]  # Last row
    total_width = 0.0
    
    for cell in bottom_row:
        if cell == 'N':
            total_width += box.width
        elif cell == 'R':
            total_width += box.length
        # Skip 'O' (empty spaces don't add to width)
    
    return total_width


def _calculate_pattern_length(grid: List[List[str]], box: Box) -> float:
    """Calculate pattern length using the first column method."""
    if not grid or not grid[0]:
        return 0.0
    
    total_length = 0.0
    
    for row in grid:
        first_cell = row[0]  # First column
        if first_cell == 'N':
            total_length += box.length
        elif first_cell == 'R':
            total_length += box.width
        # Skip 'O' (empty spaces don't add to length)
    
    return total_length


def _find_best_position(existing_placements: List[BoxPlacement], width: float, length: float, pallet: Pallet) -> tuple[float, float]:
    """
    Find the best position for a new box by pushing it up and left against existing boxes.
    
    Algorithm:
    1. Try positions from top-left, row by row
    2. For each position, check if the box fits without overlapping
    3. Return the first valid position found (top-most, then left-most)
    """
    # Start with a small step size for positioning
    step = 0.1
    
    # Try positions from top to bottom, left to right
    for y in _frange(0, pallet.length - length + step, step):
        for x in _frange(0, pallet.width - width + step, step):
            # Check if this position would cause overlap
            if not _would_overlap(x, y, width, length, existing_placements):
                # Found a valid position, but let's see if we can push it further up/left
                return _push_to_final_position(x, y, width, length, existing_placements, pallet)
    
    # Fallback: return bottom-right corner if nothing else works
    return (pallet.width - width, pallet.length - length)


def _push_to_final_position(x: float, y: float, width: float, length: float, 
                           existing_placements: List[BoxPlacement], pallet: Pallet) -> tuple[float, float]:
    """
    Push a box to its final position by moving it as far up and left as possible.
    """
    final_x, final_y = x, y
    
    # Push left as much as possible
    while final_x > 0:
        test_x = final_x - 0.1
        if test_x >= 0 and not _would_overlap(test_x, final_y, width, length, existing_placements):
            final_x = test_x
        else:
            break
    
    # Push up as much as possible
    while final_y > 0:
        test_y = final_y - 0.1
        if test_y >= 0 and not _would_overlap(final_x, test_y, width, length, existing_placements):
            final_y = test_y
        else:
            break
    
    # Snap to exact positions against existing boxes
    final_x, final_y = _snap_to_existing_boxes(final_x, final_y, width, length, existing_placements)
    
    return (final_x, final_y)


def _snap_to_existing_boxes(x: float, y: float, width: float, length: float, 
                           existing_placements: List[BoxPlacement]) -> tuple[float, float]:
    """
    Snap the box position to be exactly adjacent to existing boxes.
    """
    final_x, final_y = x, y
    
    for existing in existing_placements:
        # Check if we can snap to the right edge of an existing box
        if (abs(existing.right - x) < 0.2 and 
            not (y + length <= existing.y or y >= existing.bottom)):
            final_x = existing.right
        
        # Check if we can snap to the bottom edge of an existing box
        if (abs(existing.bottom - y) < 0.2 and 
            not (x + width <= existing.x or x >= existing.right)):
            final_y = existing.bottom
    
    return (final_x, final_y)


def _would_overlap(x: float, y: float, width: float, length: float, 
                  existing_placements: List[BoxPlacement]) -> bool:
    """
    Check if a box at the given position would overlap with any existing boxes.
    """
    for existing in existing_placements:
        if (x < existing.right and x + width > existing.x and
            y < existing.bottom and y + length > existing.y):
            return True
    return False


def _frange(start: float, stop: float, step: float):
    """
    Generate a range of floating point numbers.
    """
    current = start
    while current < stop:
        yield current
        current += step


def _convert_grid_to_placements(grid: List[List[str]], box: Box, pallet: Pallet) -> List[BoxPlacement]:
    """
    Convert a grid arrangement back to spatial placements for visualization.
    
    This is a temporary helper until we fully transition to spatial-first approach.
    """
    placements = []
    
    if not grid or not grid[0]:
        return placements
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Calculate positions based on the grid and orientations
    y = 0.0
    for row in range(rows):
        x = 0.0
        row_height = 0.0
        
        for col in range(cols):
            orientation = grid[row][col]
            
            if orientation in ['N', 'R']:
                if orientation == 'N':
                    width, length = box.width, box.length
                else:
                    width, length = box.length, box.width
                
                placements.append(BoxPlacement(x, y, width, length, orientation))
                x += width
                row_height = max(row_height, length)
            else:
                # For 'O' (empty), advance by the minimum box dimension
                x += min(box.width, box.length)
        
        y += row_height if row_height > 0 else min(box.width, box.length)
    
    return placements
