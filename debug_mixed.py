"""
Debug script for mixed orientation arrangements.
"""

from models import Box, Pallet
from utils.spatial_visualization import _convert_grid_to_spatial_placements

def test_mixed_orientations():
    """Test with a mixed orientation grid."""
    box = Box(6.0, 10.0)
    
    # Create a test grid with mixed orientations
    test_grid = [
        ['R', 'R', 'N'],
        ['R', 'R', 'N'], 
        ['N', 'N', 'O']
    ]
    
    print("Test grid:")
    for i, row in enumerate(test_grid):
        print(f"Row {i}: {' '.join(row)}")
    print()
    
    pallet = Pallet(40, 48)
    placements = _convert_grid_to_spatial_placements(test_grid, box, pallet)
    
    print("Spatial placements:")
    for i, placement in enumerate(placements):
        print(f"Box {i+1}: ({placement.x:.1f}, {placement.y:.1f}) -> ({placement.right:.1f}, {placement.bottom:.1f}) "
              f"Size: {placement.width:.1f} x {placement.length:.1f} Orientation: {placement.orientation}")

if __name__ == "__main__":
    test_mixed_orientations()
