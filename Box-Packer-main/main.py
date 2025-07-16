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

Author: Ryne Crabtree
Date: July 2025
"""

import sys
from typing import Optional
from utils import (
    get_user_input, print_arrangement, print_optimization_results, 
    print_manual_results, show_2d_layout
)
from algorithms import auto_optimize_box_count, find_best_arrangement


def main() -> None:
    """
    Main program loop for the Box Packer application.
    
    Handles user interaction and coordinates the packing process.
    """
    print("Box Packer - Optimal Pallet Arrangement Calculator")
    print("=" * 50)
    
    try:
        while True:
            # Get user input
            try:
                box, box_count = get_user_input()
            except (ValueError, KeyboardInterrupt) as e:
                if isinstance(e, KeyboardInterrupt):
                    raise
                print(f"Invalid input: {e}")
                print("Please try again.")
                continue
            
            try:
                if box_count is None:
                    # Auto-optimization mode: find optimal number of boxes
                    arrangement, rows, columns, optimal_count, final_pallet = auto_optimize_box_count(box)
                    print_optimization_results(arrangement, rows, columns, optimal_count, final_pallet)
                else:
                    # Manual mode: use provided box count
                    arrangement, rows, columns, final_pallet = find_best_arrangement(box, box_count)
                    print_manual_results(arrangement, rows, columns, final_pallet, box_count)
                
                # Display the final arrangement pattern
                print()
                print_arrangement(arrangement)
                
                # Ask about graphical visualization
                try:
                    show_graph = input("\\nWould you like to see a 2D graphical visualization? (y/n): ").strip().lower()
                    if show_graph in ['y', 'yes']:
                        print("Opening 2D graphical layout...")
                        show_2d_layout(arrangement, box, final_pallet)
                except Exception as e:
                    print(f"Error displaying visualization: {e}")
                
            except Exception as e:
                print(f"Error finding arrangement: {e}")
                print("Please try with different parameters.")
                continue
            
            # Ask if user wants to continue
            print("\\n" + "=" * 50)
            try:
                continue_choice = input("\\nWould you like to try another arrangement? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    break
            except KeyboardInterrupt:
                break
                
    except KeyboardInterrupt:
        print("\\n\\nProgram interrupted by user.")
    except Exception as e:
        print(f"\\nUnexpected error: {e}")
        print("Please report this issue if it persists.")
        sys.exit(1)
    
    print("\\nThank you for using Box Packer!")


if __name__ == "__main__":
    main()
