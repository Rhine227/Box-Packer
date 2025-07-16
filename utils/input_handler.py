"""
Input handling utilities for the Box Packer application.

This module handles user input validation and processing.
"""

from typing import Optional, Tuple
from models import Box
from config import MAX_REASONABLE_BOXES, MIN_DIMENSION, MAX_DIMENSION


def get_user_input() -> Tuple[Box, Optional[int]]:
    """
    Collect user input for box dimensions and optional box count.
    
    Returns:
        Tuple containing:
        - box: Box instance with validated dimensions
        - box_count: Number of boxes per layer (None for auto-optimization)
        
    Raises:
        ValueError: If input validation fails
    """
    # Get box dimensions with validation
    while True:
        try:
            width_input = input("Enter box width (inches): ").strip()
            if not width_input:
                raise ValueError("Width cannot be empty")
            width = float(width_input)
            if width <= 0:
                raise ValueError("Width must be positive")
            if width < MIN_DIMENSION:
                raise ValueError(f"Width must be at least {MIN_DIMENSION} inches")
            if width > MAX_DIMENSION:
                raise ValueError(f"Width must be at most {MAX_DIMENSION} inches")
            break
        except ValueError as e:
            if "could not convert" in str(e):
                print("Please enter a valid number for width.")
            else:
                print(f"Error: {e}")
    
    while True:
        try:
            length_input = input("Enter box length (inches): ").strip()
            if not length_input:
                raise ValueError("Length cannot be empty")
            length = float(length_input)
            if length <= 0:
                raise ValueError("Length must be positive")
            if length < MIN_DIMENSION:
                raise ValueError(f"Length must be at least {MIN_DIMENSION} inches")
            if length > MAX_DIMENSION:
                raise ValueError(f"Length must be at most {MAX_DIMENSION} inches")
            break
        except ValueError as e:
            if "could not convert" in str(e):
                print("Please enter a valid number for length.")
            else:
                print(f"Error: {e}")
    
    # Box class will handle dimension validation and swapping if needed
    box = Box(width, length)
    
    # Get box count with validation
    while True:
        try:
            count_input = input("Enter number of boxes per layer (or press Enter to auto-optimize): ").strip()
            if not count_input:
                box_count = None
                break
            
            box_count = int(count_input)
            if box_count <= 0:
                raise ValueError("Number of boxes must be positive")
            if box_count > MAX_REASONABLE_BOXES:
                print(f"Warning: Large number of boxes ({box_count}) may take longer to process.")
                confirm = input("Continue? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            break
        except ValueError as e:
            if "invalid literal" in str(e):
                print("Please enter a valid integer for box count.")
            else:
                print(f"Error: {e}")
    
    return box, box_count
