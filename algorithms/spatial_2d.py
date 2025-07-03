"""
2D Spatial arrangement algorithms for finding optimal box patterns.

This module uses a 2D placement approach rather than rigid grid thinking,
allowing for more creative and efficient patterns by considering actual
box positions and dimensions.
"""

from typing import List, Tuple, Optional, Set
from models import Box, Pallet
import math


class BoxPlacement:
    """Represents a placed box with its position and orientation."""
    def __init__(self, x: float, y: float, width: float, length: float, orientation: str):
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.orientation = orientation  # 'N' or 'R'
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def bottom(self) -> float:
        return self.y + self.length


def find_2d_spatial_arrangement(box: Box, box_count: int, pallet: Pallet) -> Optional[List[List[str]]]:
    """
    Find optimal arrangement using 2D spatial placement algorithm.
    
    This approach:
    1. Places boxes in actual 2D space
    2. Tries different orientations and positions
    3. Uses spatial optimization rather than grid constraints
    4. Allows for more creative patterns
    
    Args:
        box: Box instance with dimensions
        box_count: Target number of boxes to place
        pallet: Pallet constraints
        
    Returns:
        2D grid representation of the best arrangement found, or None
    """
    best_placement = None
    best_efficiency = 0
    
    # Try different starting strategies
    strategies = [
        _strategy_bottom_left_fill,
        _strategy_mixed_orientation_blocks,
        _strategy_user_inspired_pattern,
        _strategy_efficiency_optimized,
    ]
    
    for strategy in strategies:
        placement = strategy(box, box_count, pallet)
        if placement and len(placement) >= box_count:
            # Calculate efficiency
            total_area = sum(p.width * p.length for p in placement)
            efficiency = len(placement) / pallet.area
            
            if efficiency > best_efficiency:
                best_placement = placement
                best_efficiency = efficiency
    
    if best_placement:
        return _convert_placement_to_grid(best_placement, box, pallet)
    
    return None


def _strategy_bottom_left_fill(box: Box, box_count: int, pallet: Pallet) -> List[BoxPlacement]:
    """Bottom-left fill algorithm with smart orientation choices."""
    placements = []
    
    y = 0
    while y < pallet.length and len(placements) < box_count:
        x = 0
        row_height = 0
        
        while x < pallet.width and len(placements) < box_count:
            # Try both orientations and pick the better one
            normal_fits = (x + box.width <= pallet.width and y + box.length <= pallet.length)
            rotated_fits = (x + box.length <= pallet.width and y + box.width <= pallet.length)
            
            if normal_fits and rotated_fits:
                # Both fit, choose based on space efficiency
                remaining_width = pallet.width - x
                remaining_length = pallet.length - y
                
                # Prefer orientation that uses space more efficiently
                normal_waste = remaining_width * remaining_length - box.width * box.length
                rotated_waste = remaining_width * remaining_length - box.length * box.width
                
                if rotated_waste < normal_waste:
                    # Use rotated
                    placements.append(BoxPlacement(x, y, box.length, box.width, 'R'))
                    x += box.length
                    row_height = max(row_height, box.width)
                else:
                    # Use normal
                    placements.append(BoxPlacement(x, y, box.width, box.length, 'N'))
                    x += box.width
                    row_height = max(row_height, box.length)
            elif normal_fits:
                placements.append(BoxPlacement(x, y, box.width, box.length, 'N'))
                x += box.width
                row_height = max(row_height, box.length)
            elif rotated_fits:
                placements.append(BoxPlacement(x, y, box.length, box.width, 'R'))
                x += box.length
                row_height = max(row_height, box.width)
            else:
                break  # No more boxes fit in this row
        
        y += row_height if row_height > 0 else min(box.width, box.length)
    
    return placements


def _strategy_mixed_orientation_blocks(box: Box, box_count: int, pallet: Pallet) -> List[BoxPlacement]:
    """Create blocks of same orientation, then fill gaps."""
    placements = []
    
    # Start with blocks of rotated boxes (often more efficient)
    block_width = box.length * 2  # 2 boxes wide
    block_length = box.width * 2  # 2 boxes tall
    
    y = 0
    while y + block_length <= pallet.length and len(placements) < box_count:
        x = 0
        while x + block_width <= pallet.width and len(placements) < box_count:
            # Place 2x2 block of rotated boxes
            for by in range(2):
                for bx in range(2):
                    if len(placements) < box_count:
                        placements.append(BoxPlacement(
                            x + bx * box.length, 
                            y + by * box.width, 
                            box.length, box.width, 'R'
                        ))
            x += block_width
        y += block_length
    
    # Fill remaining space with normal orientation
    for p in placements:
        # Mark occupied space
        pass
    
    # Simple fill for remaining boxes
    remaining = box_count - len(placements)
    if remaining > 0:
        additional = _strategy_bottom_left_fill(box, remaining, pallet)
        # Filter out overlapping placements
        for new_placement in additional:
            if not _overlaps_with_existing(new_placement, placements):
                placements.append(new_placement)
                if len(placements) >= box_count:
                    break
    
    return placements


def _strategy_user_inspired_pattern(box: Box, box_count: int, pallet: Pallet) -> List[BoxPlacement]:
    """Try to recreate patterns similar to the user's discovery."""
    placements = []
    
    # Only apply for appropriate dimensions and counts
    if not (6.0 <= box.width <= 6.5 and 8.0 <= box.length <= 9.0 and 30 <= box_count <= 35):
        return placements
    
    # Try the user's pattern style: mixed orientations with strategic gaps
    pattern_positions = [
        # First 4 rows: R R N N R pattern
        (0, 0, 'R'), (box.length, 0, 'R'), (box.length*2, 0, 'N'), (box.length*2 + box.width, 0, 'N'), (box.length*2 + box.width*2, 0, 'R'),
        (0, box.width, 'R'), (box.length, box.width, 'R'), (box.length*2, box.width, 'N'), (box.length*2 + box.width, box.width, 'N'), (box.length*2 + box.width*2, box.width, 'R'),
        (0, box.width*2, 'R'), (box.length, box.width*2, 'R'), (box.length*2, box.width*2, 'N'), (box.length*2 + box.width, box.width*2, 'N'), (box.length*2 + box.width*2, box.width*2, 'R'),
        (0, box.width*3, 'R'), (box.length, box.width*3, 'R'), (box.length*2, box.width*3, 'N'), (box.length*2 + box.width, box.width*3, 'N'), (box.length*2 + box.width*2, box.width*3, 'R'),
        
        # Next 2 rows: R R O O R pattern (with strategic gaps)
        (0, box.width*4, 'R'), (box.length, box.width*4, 'R'), (box.length*2 + box.width*2, box.width*4, 'R'),
        (0, box.width*5, 'R'), (box.length, box.width*5, 'R'), (box.length*2 + box.width*2, box.width*5, 'R'),
        
        # Bottom row: N N N N N N pattern
        (0, box.width*6, 'N'), (box.width, box.width*6, 'N'), (box.width*2, box.width*6, 'N'), 
        (box.width*3, box.width*6, 'N'), (box.width*4, box.width*6, 'N'), (box.width*5, box.width*6, 'N'),
    ]
    
    for x, y, orientation in pattern_positions:
        if len(placements) >= box_count:
            break
        
        if orientation == 'N':
            width, length = box.width, box.length
        else:
            width, length = box.length, box.width
        
        # Check if it fits
        if x + width <= pallet.width and y + length <= pallet.length:
            placements.append(BoxPlacement(x, y, width, length, orientation))
    
    return placements


def _strategy_efficiency_optimized(box: Box, box_count: int, pallet: Pallet) -> List[BoxPlacement]:
    """Optimize for maximum space efficiency."""
    placements = []
    
    # Calculate optimal mix of orientations
    normal_area = box.width * box.length
    rotated_area = box.length * box.width  # Same area, but different fit characteristics
    
    # Try to minimize wasted space
    best_placements = []
    
    # Try different ratios of normal to rotated
    for normal_ratio in [0.0, 0.25, 0.5, 0.75, 1.0]:
        test_placements = []
        normal_count = int(box_count * normal_ratio)
        rotated_count = box_count - normal_count
        
        # Place normal boxes first
        y = 0
        placed_normal = 0
        while y + box.length <= pallet.length and placed_normal < normal_count:
            x = 0
            while x + box.width <= pallet.width and placed_normal < normal_count:
                test_placements.append(BoxPlacement(x, y, box.width, box.length, 'N'))
                x += box.width
                placed_normal += 1
            y += box.length
        
        # Place rotated boxes in remaining space
        placed_rotated = 0
        for y_pos in range(0, int(pallet.length - box.width + 1), int(box.width)):
            for x_pos in range(0, int(pallet.width - box.length + 1), int(box.length)):
                if placed_rotated >= rotated_count:
                    break
                
                # Check if this position overlaps with existing placements
                new_placement = BoxPlacement(x_pos, y_pos, box.length, box.width, 'R')
                if not _overlaps_with_existing(new_placement, test_placements):
                    test_placements.append(new_placement)
                    placed_rotated += 1
        
        if len(test_placements) > len(best_placements):
            best_placements = test_placements
    
    return best_placements


def _overlaps_with_existing(new_placement: BoxPlacement, existing: List[BoxPlacement]) -> bool:
    """Check if a new placement overlaps with existing placements."""
    for existing_placement in existing:
        if (new_placement.x < existing_placement.right and 
            new_placement.right > existing_placement.x and
            new_placement.y < existing_placement.bottom and
            new_placement.bottom > existing_placement.y):
            return True
    return False


def _convert_placement_to_grid(placements: List[BoxPlacement], box: Box, pallet: Pallet) -> List[List[str]]:
    """Convert 2D placements back to grid representation for display."""
    if not placements:
        return []
    
    # Determine grid size based on actual placements
    max_x = max(p.right for p in placements)
    max_y = max(p.bottom for p in placements)
    
    # Create grid with appropriate resolution
    grid_width = max(6, math.ceil(max_x / min(box.width, box.length)))
    grid_height = max(6, math.ceil(max_y / min(box.width, box.length)))
    
    # Initialize grid
    grid = [['O' for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Fill grid based on placements
    box_number = 1
    for placement in placements:
        # Find grid position
        grid_x = int(placement.x / min(box.width, box.length))
        grid_y = int(placement.y / min(box.width, box.length))
        
        # Place box in grid (simplified mapping)
        if 0 <= grid_y < grid_height and 0 <= grid_x < grid_width:
            grid[grid_y][grid_x] = placement.orientation
        
        box_number += 1
    
    return grid
