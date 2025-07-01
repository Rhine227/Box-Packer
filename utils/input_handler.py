"""
Input handling utilities for the Box Packer application.

This module handles user input validation and processing.
"""

from typing import Optional, Tuple
from models import Box


def get_user_input() -> Tuple[Box, Optional[int]]:
    """
    Collect user input for box dimensions and optional box count.
    
    Returns:
        Tuple containing:
        - box: Box instance with validated dimensions
        - box_count: Number of boxes per layer (None for auto-optimization)
    """
    width = float(input("Enter box width: "))
    length = float(input("Enter box length: "))
    
    # Box class will handle dimension validation and swapping if needed
    box = Box(width, length)
    
    count_input = input("Enter number of boxes per layer (or press Enter to auto-optimize): ").strip()
    box_count = int(count_input) if count_input else None
    
    return box, box_count
