"""
Pallet model for representing pallet dimensions and constraints.

This module defines the Pallet class which handles pallet dimensions,
area calculations, and constraint checking.
"""

from config import PALLET_WIDTH, PALLET_LENGTH


class Pallet:
    """
    Represents a rectangular pallet with width and length dimensions.
    
    Provides methods for calculating area and checking if arrangements fit.
    """
    
    def __init__(self, width: float = PALLET_WIDTH, length: float = PALLET_LENGTH):
        """
        Initialize a pallet with width and length dimensions.
        
        Args:
            width: The width of the pallet (default: standard pallet width)
            length: The length of the pallet (default: standard pallet length)
        """
        self.width = width
        self.length = length
    
    @property
    def area(self) -> float:
        """Calculate and return the area of the pallet."""
        return self.width * self.length
    
    @property
    def is_standard_size(self) -> bool:
        """Check if this pallet is the standard size."""
        return self.width == PALLET_WIDTH and self.length == PALLET_LENGTH
    
    def scale(self, factor: float) -> 'Pallet':
        """
        Create a new pallet scaled by the given factor.
        
        Args:
            factor: Scale factor to apply to both dimensions
            
        Returns:
            New Pallet instance with scaled dimensions
        """
        return Pallet(self.width * factor, self.length * factor)
    
    def __str__(self) -> str:
        """String representation of the pallet."""
        return f"Pallet({self.width} x {self.length})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the pallet."""
        return f"Pallet(width={self.width}, length={self.length}, area={self.area})"
