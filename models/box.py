"""
Box model for representing individual boxes with their dimensions.

This module defines the Box class which handles box dimensions,
validation, and orientation logic.
"""

from typing import Tuple


class Box:
    """
    Represents a rectangular box with width and length dimensions.
    
    Ensures that width is always the shorter dimension and length is the longer dimension.
    Provides methods for calculating area and handling rotations.
    """
    
    def __init__(self, width: float, length: float):
        """
        Initialize a box with width and length dimensions.
        
        Args:
            width: The width dimension of the box
            length: The length dimension of the box
            
        Note: If width > length, dimensions will be automatically swapped
              and a warning will be displayed.
        """
        self.width, self.length = self._validate_dimensions(width, length)
    
    def _validate_dimensions(self, width: float, length: float) -> Tuple[float, float]:
        """
        Validate that width <= length, swapping if necessary.
        
        Args:
            width: Proposed width dimension
            length: Proposed length dimension
            
        Returns:
            Tuple of (validated_width, validated_length)
        """
        if width > length:
            print(f"WARNING: You entered width ({width}) > length ({length}). That's stupid!")
            print("Automatically swapping them so width is the shorter dimension.")
            width, length = length, width
            print(f"Corrected dimensions: width = {width}, length = {length}")
        
        return width, length
    
    @property
    def area(self) -> float:
        """Calculate and return the area of the box."""
        return self.width * self.length
    
    def get_dimensions_for_orientation(self, orientation: str) -> Tuple[float, float]:
        """
        Get the effective width and height for a given orientation.
        
        Args:
            orientation: 'N' for normal, 'R' for rotated
            
        Returns:
            Tuple of (effective_width, effective_height) for the given orientation
        """
        if orientation == 'N':
            # Normal: width is left-right, length is up-down
            return self.width, self.length
        elif orientation == 'R':
            # Rotated: length is left-right, width is up-down
            return self.length, self.width
        else:
            raise ValueError(f"Invalid orientation: {orientation}. Must be 'N' or 'R'")
    
    def __str__(self) -> str:
        """String representation of the box."""
        return f"Box({self.width} x {self.length})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the box."""
        return f"Box(width={self.width}, length={self.length}, area={self.area})"
