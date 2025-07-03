"""
Box Packer Program - Optimal Pallet Arrangement Calculator

This program arranges rectangular boxes into the most efficient pattern for a layer on a wooden pallet.
The program follows these key principles:
- Uses spatial 2D placement algorithms for optimal packing efficiency
- Boxes are positioned using actual coordinates and butted against each other
- Boxes can be rotated 90° for better space utilization
- Visual representation shows exact spatial positioning without artificial grid constraints

Features:
- Automatic optimization to find the maximum number of boxes that fit
- Manual mode to test specific box counts
- Interactive 2D graphical visualization with matplotlib
- True spatial positioning where boxes are pushed up and left against adjacent boxes
- Professional visualization with proper scaling and measurements

Author: Generated with assistance
Date: July 2025
"""

from utils import get_user_input
from utils.spatial_display import print_optimization_results_spatial, print_manual_results_spatial
from utils.spatial_visualization import show_spatial_layout, create_spatial_arrangement
from algorithms import auto_optimize_box_count, find_best_arrangement


def main():
    """
    Main program loop for the Box Packer application.
    
    Handles user interaction and coordinates the packing process.
    """
    print("Box Packer - Optimal Pallet Arrangement Calculator")
    print("=" * 50)
    
    try:
        while True:
            # Get user input
            box, box_count = get_user_input()
            
            if box_count is None:
                # Auto-optimization mode: find optimal number of boxes
                arrangement, rows, columns, optimal_count, final_pallet = auto_optimize_box_count(box)
                print_optimization_results_spatial(optimal_count, final_pallet)
            else:
                # Manual mode: use provided box count
                arrangement, rows, columns, final_pallet = find_best_arrangement(box, box_count)
                print_manual_results_spatial(final_pallet, box_count)
            
            
            # Display spatial visualization directly
            print("Opening spatial 2D graphical layout...")
            if box_count is None:
                show_spatial_layout(box, optimal_count, final_pallet, arrangement)
            else:
                show_spatial_layout(box, box_count, final_pallet, arrangement)
            
            # Ask if user wants to continue
            print("\\n" + "=" * 50)
            continue_choice = input("\\nWould you like to try another arrangement? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                break
                
    except KeyboardInterrupt:
        print("\\n\\nProgram interrupted by user.")
    except Exception as e:
        print(f"\\nAn error occurred: {e}")
        print("Please check your inputs and try again.")
    
    print("\\nThank you for using Box Packer!")


if __name__ == "__main__":
    main()
