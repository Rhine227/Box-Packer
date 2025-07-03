"""
Debug the 32-box arrangement to see the exact layout.
"""

from models import Box, Pallet
from utils.spatial_visualization import _convert_grid_to_spatial_placements, _calculate_pattern_width, _calculate_pattern_length
from algorithms import find_best_arrangement

def debug_32_box_arrangement():
    """Show the 32-box arrangement details."""
    box = Box(6.3, 8.5)
    box_count = 32
    
    print(f"Testing with {box_count} boxes of size {box.width} x {box.length}")
    print()
    
    # Get the arrangement
    arrangement, rows, columns, final_pallet = find_best_arrangement(box, box_count)
    
    print(f"Grid arrangement ({rows} rows x {columns} columns):")
    for i, row in enumerate(arrangement):
        print(f"Row {i}: {' '.join(row)}")
    print()
    
    # Calculate pattern dimensions
    pattern_width = _calculate_pattern_width(arrangement, box)
    pattern_length = _calculate_pattern_length(arrangement, box)
    print(f"Pattern dimensions: {pattern_width:.1f} x {pattern_length:.1f}")
    print(f"Pallet dimensions: {final_pallet.width} x {final_pallet.length}")
    print(f"Fits on pallet: {pattern_width <= final_pallet.width and pattern_length <= final_pallet.length}")
    print()
    
    # Convert to spatial placements
    placements = _convert_grid_to_spatial_placements(arrangement, box, final_pallet)
    
    print(f"Spatial placements ({len(placements)} boxes):")
    for i, placement in enumerate(placements):
        print(f"Box {i+1:2d}: ({placement.x:5.1f}, {placement.y:5.1f}) -> ({placement.right:5.1f}, {placement.bottom:5.1f}) "
              f"Size: {placement.width:4.1f} x {placement.length:4.1f} {placement.orientation}")
    
    # Check the actual dimensions of the placement
    if placements:
        max_x = max(p.right for p in placements)
        max_y = max(p.bottom for p in placements)
        print(f"\nActual placement dimensions: {max_x:.1f} x {max_y:.1f}")
        print(f"Efficiency: {len(placements) * box.width * box.length / (final_pallet.width * final_pallet.length) * 100:.1f}%")

if __name__ == "__main__":
    debug_32_box_arrangement()
    
    box = Box(6.3, 8.5)
    pallet = Pallet()  # Standard 40x48
    box_count = 32
    
    print("Debugging advanced pattern search...")
    print(f"Box: {box.width} x {box.length}")
    print(f"Target: {box_count} boxes")
    print(f"Pallet: {pallet.width} x {pallet.length}")
    print()
    
    # Try the advanced pattern search
    result = try_mixed_pattern_arrangement(box, box_count, pallet, max_rows=10, max_cols=10)
    
    if result:
        print("SUCCESS: Found advanced pattern!")
        box_count_found = sum(1 for row in result for cell in row if cell in ['N', 'R'])
        print(f"Pattern has {box_count_found} boxes")
        print("Pattern:")
        for row in result:
            print(" ".join(row))
    else:
        print("FAILED: No advanced pattern found")
    
    return result

if __name__ == "__main__":
    debug_advanced_search()
