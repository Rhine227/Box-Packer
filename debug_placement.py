"""
Debug script to see exactly where boxes are being placed.
"""

from models import Box, Pallet
from utils.spatial_visualization import _convert_grid_to_spatial_placements
from algorithms import find_best_arrangement

def debug_box_placement():
    """Show exactly where each box is placed."""
    box = Box(8.0, 10.0)
    pallet = Pallet(40, 48)
    box_count = 6
    
    print(f"Testing with {box_count} boxes of size {box.width} x {box.length}")
    print(f"Pallet size: {pallet.width} x {pallet.length}")
    print()
    
    # Get the arrangement
    arrangement, rows, columns, final_pallet = find_best_arrangement(box, box_count)
    
    print("Grid arrangement:")
    for i, row in enumerate(arrangement):
        print(f"Row {i}: {' '.join(row)}")
    print()
    
    # Convert to spatial placements
    placements = _convert_grid_to_spatial_placements(arrangement, box, pallet)
    
    print("Spatial placements:")
    for i, placement in enumerate(placements):
        print(f"Box {i+1}: ({placement.x:.1f}, {placement.y:.1f}) -> ({placement.right:.1f}, {placement.bottom:.1f}) "
              f"Size: {placement.width:.1f} x {placement.length:.1f} Orientation: {placement.orientation}")
    
    print()
    print("Checking for gaps:")
    # Check if boxes are actually butted together
    for i, p1 in enumerate(placements):
        for j, p2 in enumerate(placements):
            if i != j:
                # Check if they should be adjacent horizontally
                if abs(p1.right - p2.x) < 0.1 and not (p1.bottom <= p2.y or p1.y >= p2.bottom):
                    print(f"Box {i+1} and Box {j+1} are horizontally adjacent (good!)")
                elif abs(p1.x - p2.right) < 0.1 and not (p1.bottom <= p2.y or p1.y >= p2.bottom):
                    print(f"Box {j+1} and Box {i+1} are horizontally adjacent (good!)")
                
                # Check if they should be adjacent vertically  
                if abs(p1.bottom - p2.y) < 0.1 and not (p1.right <= p2.x or p1.x >= p2.right):
                    print(f"Box {i+1} and Box {j+1} are vertically adjacent (good!)")
                elif abs(p1.y - p2.bottom) < 0.1 and not (p1.right <= p2.x or p1.x >= p2.right):
                    print(f"Box {j+1} and Box {i+1} are vertically adjacent (good!)")

if __name__ == "__main__":
    debug_box_placement()
