"""
Visualization utilities for the Box Packer application.

This module provides graphical 2D representations of box arrangements
on pallets using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List
from models import Box, Pallet


def show_2d_layout(arrangement: List[List[str]], box: Box, pallet: Pallet):
    """
    Display a 2D graphical representation of the box arrangement.
    
    Features:
    - Dark blue background
    - Orange rectangle for the pallet
    - Grey boxes for each box with numbers
    - Boxes numbered top to bottom, left to right
    
    Args:
        arrangement: 2D grid of box orientations ('N', 'R', 'O')
        box: Box instance with dimensions
        pallet: Pallet instance with dimensions
    """
    if not arrangement or not arrangement[0]:
        print("No arrangement to display")
        return
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Set dark blue background
    fig.patch.set_facecolor('#1e3a5f')  # Dark blue
    ax.set_facecolor('#1e3a5f')  # Dark blue
    
    # Draw pallet as orange rectangle
    pallet_rect = patches.Rectangle(
        (0, 0), pallet.width, pallet.length,
        linewidth=3, edgecolor='orange', facecolor='orange', alpha=0.3
    )
    ax.add_patch(pallet_rect)
    
    # Get arrangement dimensions
    rows = len(arrangement)
    columns = len(arrangement[0])
    
    # Calculate box positions and draw boxes
    box_number = 1
    
    for row in range(rows):
        for col in range(columns):
            orientation = arrangement[row][col]
            
            if orientation in ['N', 'R']:  # Skip empty spaces ('O')
                # Calculate position based on orientation
                if orientation == 'N':
                    # Normal: box width horizontal, box length vertical
                    box_width = box.width
                    box_height = box.length
                else:  # orientation == 'R'
                    # Rotated: box length horizontal, box width vertical
                    box_width = box.length
                    box_height = box.width
                
                # Position the box
                x = col * box_width
                y = row * box_height
                
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
    ax.set_title(f'Box Arrangement on Pallet ({rows}×{columns})', 
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


def show_arrangement_comparison(arrangements: List[tuple], box: Box, pallet: Pallet):
    """
    Display multiple arrangements side by side for comparison.
    
    Args:
        arrangements: List of tuples (arrangement, rows, columns, title)
        box: Box instance with dimensions
        pallet: Pallet instance with dimensions
    """
    if not arrangements:
        print("No arrangements to compare")
        return
    
    num_arrangements = len(arrangements)
    fig, axes = plt.subplots(1, num_arrangements, figsize=(6 * num_arrangements, 8))
    
    if num_arrangements == 1:
        axes = [axes]  # Make it iterable
    
    # Set dark blue background
    fig.patch.set_facecolor('#1e3a5f')
    
    for idx, (arrangement, rows, columns, title) in enumerate(arrangements):
        ax = axes[idx]
        ax.set_facecolor('#1e3a5f')
        
        # Draw pallet
        pallet_rect = patches.Rectangle(
            (0, 0), pallet.width, pallet.length,
            linewidth=3, edgecolor='orange', facecolor='orange', alpha=0.3
        )
        ax.add_patch(pallet_rect)
        
        # Draw boxes
        box_number = 1
        for row in range(rows):
            for col in range(columns):
                orientation = arrangement[row][col]
                
                if orientation in ['N', 'R']:
                    if orientation == 'N':
                        box_width = box.width
                        box_height = box.length
                    else:
                        box_width = box.length
                        box_height = box.width
                    
                    x = col * box_width
                    y = row * box_height
                    
                    box_rect = patches.Rectangle(
                        (x, y), box_width, box_height,
                        linewidth=2, edgecolor='black', facecolor='lightgrey', alpha=0.8
                    )
                    ax.add_patch(box_rect)
                    
                    center_x = x + box_width / 2
                    center_y = y + box_height / 2
                    
                    ax.text(center_x, center_y, str(box_number), 
                           ha='center', va='center', fontsize=10, fontweight='bold', color='black')
                    
                    box_number += 1
        
        # Set axis properties
        ax.set_xlim(-1, pallet.width + 1)
        ax.set_ylim(-1, pallet.length + 1)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.set_title(title, fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3, color='white')
    
    plt.tight_layout()
    plt.show()
