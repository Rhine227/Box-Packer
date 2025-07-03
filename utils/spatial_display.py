"""
Simplified display utilities for spatial Box Packer application.

This module provides result reporting without text-based arrangement patterns.
"""

from typing import List
from models import Pallet


def print_optimization_results_spatial(optimal_count: int, pallet: Pallet) -> None:
    """
    Print the results of auto-optimization without text arrangement.
    
    Args:
        optimal_count: Optimal number of boxes per layer
        pallet: Final pallet used
    """
    print(f"\nOptimal boxes per layer: {optimal_count}")
    
    # Show pallet size information
    if not pallet.is_standard_size:
        from config import PALLET_WIDTH, PALLET_LENGTH
        print(f"Final pallet size: {pallet.width:.1f} x {pallet.length:.1f}")
        scale_factor = pallet.width / PALLET_WIDTH
        print(f"Scale factor: {scale_factor:.1f}x original size")
    else:
        print(f"Pallet size: {pallet.width} x {pallet.length} (original)")


def print_manual_results_spatial(pallet: Pallet, box_count: int) -> None:
    """
    Print the results of manual box count specification without text arrangement.
    
    Args:
        pallet: Final pallet used
        box_count: User-specified box count
    """
    print(f"\nTargeted arrangement: {box_count} boxes")
    
    if not pallet.is_standard_size:
        from config import PALLET_WIDTH, PALLET_LENGTH
        print(f"WARNING: Your requested {box_count} boxes required a larger pallet!")
        print(f"Final pallet size: {pallet.width:.1f} x {pallet.length:.1f}")
        scale_factor = pallet.width / PALLET_WIDTH
        print(f"Scale factor: {scale_factor:.1f}x original size")
        pallet_area_increase = pallet.area / (PALLET_WIDTH * PALLET_LENGTH)
        print(f"Pallet area increased by {pallet_area_increase:.1f}x")
    else:
        print(f"Pallet size: {pallet.width} x {pallet.length}")
