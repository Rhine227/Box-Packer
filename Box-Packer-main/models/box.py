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
            
        Raises:
            ValueError: If dimensions are invalid (negative or zero)
            
        Note: If width > length, dimensions will be automatically swapped
              and a warning will be displayed.
        """
        if width <= 0 or length <= 0:
            raise ValueError("Box dimensions must be positive")
        
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
            print(f"WARNING: You entered width ({width}) > length ({length}).")
            print("Automatically swapping them so width is the shorter dimension.")
            width, length = length, width
            print(f"Corrected dimensions: width = {width}, length = {length}")
        
        return width, length
    
    @property
    def area(self) -> float:
        """Calculate and return the area of the box."""
        return self.width * self.length
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate and return the aspect ratio (length/width)."""
        return self.length / self.width if self.width > 0 else 0
    
    def get_dimensions_for_orientation(self, orientation: str) -> Tuple[float, float]:
        """
        Get the effective width and height for a given orientation.
        
        Args:
            orientation: 'N' for normal, 'R' for rotated
            
        Returns:
            Tuple of (effective_width, effective_height) for the given orientation
            
        Raises:
            ValueError: If orientation is not 'N' or 'R'
        """
        if orientation == 'N':
            # Normal: width is left-right, length is up-down
            return self.width, self.length
        elif orientation == 'R':
            # Rotated: length is left-right, width is up-down
            return self.length, self.width
        else:
            raise ValueError(f"Invalid orientation: {orientation}. Must be 'N' or 'R'")
    
    def can_fit_in_space(self, available_width: float, available_height: float) -> bool:
        """
        Check if the box can fit in the given space in any orientation.
        
        Args:
            available_width: Available width space
            available_height: Available height space
            
        Returns:
            True if box can fit in either orientation
        """
        # Normal orientation
        normal_fits = self.width <= available_width and self.length <= available_height
        # Rotated orientation
        rotated_fits = self.length <= available_width and self.width <= available_height
        
        return normal_fits or rotated_fits
    
    def best_orientation_for_space(self, available_width: float, available_height: float) -> str:
        """
        Determine the best orientation for the given space.
        
        Args:
            available_width: Available width space
            available_height: Available height space
            
        Returns:
            'N' for normal, 'R' for rotated, or raises ValueError if doesn't fit
            
        Raises:
            ValueError: If box doesn't fit in either orientation
        """
        normal_fits = self.width <= available_width and self.length <= available_height
        rotated_fits = self.length <= available_width and self.width <= available_height
        
        if not normal_fits and not rotated_fits:
            raise ValueError(f"Box doesn't fit in space {available_width}x{available_height}")
        
        if normal_fits and rotated_fits:
            # Both orientations fit, choose the one with better space utilization
            normal_efficiency = (self.width * self.length) / (available_width * available_height)
            rotated_efficiency = (self.length * self.width) / (available_width * available_height)
            return 'N' if normal_efficiency >= rotated_efficiency else 'R'
        
        return 'N' if normal_fits else 'R'
    
    def __str__(self) -> str:
        """String representation of the box."""
        return f"Box({self.width} x {self.length})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the box."""
        return f"Box(width={self.width}, length={self.length}, area={self.area})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another box."""
        if not isinstance(other, Box):
            return False
        return self.width == other.width and self.length == other.length
    
    def __hash__(self) -> int:
        """Hash function for use in sets and as dict keys."""
        return hash((self.width, self.length))
