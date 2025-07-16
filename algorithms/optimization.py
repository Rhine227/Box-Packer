"""
Optimization algorithms for the Box Packer application.

This module contains algorithms for finding optimal arrangements
and automatically determining the best number of boxes per layer.
"""

from typing import Tuple, List
from models import Box, Pallet
from .arrangement import generate_candidates, try_arrangement, find_best_arrangement_with_custom_pallet, try_flexible_arrangement, try_smart_patterns
from .scaling import find_best_arrangement_with_scaling, find_best_arrangement_fine_scaling
from utils.geometry import calculate_arrangement_area, ratio_score
from config import PALLET_WIDTH, PALLET_LENGTH


def find_best_arrangement(box: Box, box_count: int) -> Tuple[List[List[str]], int, int, Pallet]:
    """
    Find the best arrangement for a specific number of boxes.
    
    This is the main function for finding arrangements. It:
    1. Tries different arrangements on the standard pallet
    2. If nothing fits, automatically scales up the pallet size
    3. Provides detailed debugging information about the process
    
    Args:
        box: Box instance with dimensions
        box_count: Number of boxes to arrange
        
    Returns:
        Tuple containing:
        - arrangement: 2D grid of box orientations
        - rows: Number of rows in arrangement
        - columns: Number of columns in arrangement
        - pallet: Pallet instance used
        
    Note: May return scaled pallet if standard size insufficient
    """
    from utils.display import print_box_info, print_program_header
    
    print_box_info(box, box_count)
    print_program_header()
    
    candidates = generate_candidates(box_count)
    print(f"Trying {len(candidates)} different arrangements...")
    
    standard_pallet = Pallet()
    standard_pallet_area = standard_pallet.area
    
    # Also try flexible arrangement algorithm
    print("Trying flexible arrangement algorithm...")
    flexible_arrangement = try_flexible_arrangement(box, box_count, standard_pallet)
    
    # Try smart patterns
    print("Trying smart patterns...")
    smart_arrangement = try_smart_patterns(box, box_count, standard_pallet)
    
    # Compare all arrangements and pick the best
    candidates_to_compare = []
    
    if flexible_arrangement is not None:
        flexible_area = calculate_arrangement_area(flexible_arrangement, box)
        flexible_rows = len(flexible_arrangement)
        flexible_columns = len(flexible_arrangement[0]) if flexible_rows > 0 else 0
        flexible_ratio_score = ratio_score(flexible_rows, flexible_columns)
        area_efficiency = min(flexible_area / standard_pallet.area, standard_pallet.area / flexible_area)
        combined_score = (1.0 - area_efficiency) * 1000 + flexible_ratio_score
        candidates_to_compare.append(("flexible", flexible_arrangement, flexible_area, combined_score, flexible_rows, flexible_columns))
        print(f"  Flexible algorithm: SUCCESS with {flexible_rows} rows x {flexible_columns} columns, area: {flexible_area:.2f}, efficiency: {area_efficiency:.3f}")
    else:
        print("  Flexible algorithm: FAILED")
    
    if smart_arrangement is not None:
        smart_area = calculate_arrangement_area(smart_arrangement, box)
        smart_rows = len(smart_arrangement)
        smart_columns = len(smart_arrangement[0]) if smart_rows > 0 else 0
        smart_ratio_score = ratio_score(smart_rows, smart_columns)
        area_efficiency = min(smart_area / standard_pallet.area, standard_pallet.area / smart_area)
        combined_score = (1.0 - area_efficiency) * 1000 + smart_ratio_score
        candidates_to_compare.append(("smart", smart_arrangement, smart_area, combined_score, smart_rows, smart_columns))
        print(f"  Smart patterns: SUCCESS with {smart_rows} rows x {smart_columns} columns, area: {smart_area:.2f}, efficiency: {area_efficiency:.3f}")
    else:
        print("  Smart patterns: FAILED")
    
    # Initialize best
    if candidates_to_compare:
        # Pick the best candidate (smart patterns have priority)
        best_candidate = min(candidates_to_compare, key=lambda x: x[3])  # Sort by combined score
        _, best_arrangement, best_area, best_score, best_rows, best_columns = best_candidate
        print(f"Using {best_candidate[0]} algorithm as best solution so far")
    else:
        best_arrangement = None
        best_area = None
        best_score = float('inf')
        best_rows = 0
        best_columns = 0
    
    # Only try traditional grid methods if no smart patterns worked, or if they might be better
    print("Trying traditional grid arrangements...")
    traditional_tried = 0
    
    for rows, columns in candidates:
        arrangement = try_arrangement(rows, columns, box, box_count, standard_pallet)
        if arrangement is None:
            print(f"  Failed: {rows} rows x {columns} columns")
            continue
            
        traditional_tried += 1
        area = calculate_arrangement_area(arrangement, box)
        ratio_score_val = ratio_score(rows, columns)
        
        # Calculate how close this arrangement's area is to the standard pallet area
        area_efficiency = min(area / standard_pallet_area, standard_pallet_area / area)
        
        # Combined score: prioritize area efficiency first, then ratio score
        combined_score = (1.0 - area_efficiency) * 1000 + ratio_score_val
        
        print(f"  Traditional: {rows} rows x {columns} columns, area: {area:.2f}, efficiency: {area_efficiency:.3f}, score: {combined_score:.1f}")
        
        # Only replace smart pattern if traditional is significantly better
        # Add a penalty to traditional methods to prefer smart patterns
        traditional_score = combined_score + 50  # Penalty for traditional methods
        
        if traditional_score < best_score:
            print(f"    Traditional method beats smart patterns! Updating best solution.")
            best_arrangement = arrangement
            best_area = area
            best_score = combined_score  # Use actual score, not penalized
            best_rows = rows
            best_columns = columns
        else:
            print(f"    Smart pattern remains better (smart: {best_score:.1f} vs traditional: {traditional_score:.1f})")
    
    if traditional_tried == 0:
        print("  No traditional arrangements worked")

    # If no arrangement worked on standard pallet, try scaling
    if best_arrangement is None:
        # Provide helpful error analysis
        min_area_needed = box.area * box_count
        pallet_area_available = standard_pallet.area
        
        print(f"\\nError Analysis:")
        print(f"Minimum area needed for all boxes: {min_area_needed:.2f}")
        print(f"Available pallet area: {pallet_area_available:.2f}")
        
        if min_area_needed > pallet_area_available:
            print("The total area of all boxes exceeds the pallet area.")
        else:
            print("The boxes don't fit due to dimensional constraints.")
            
        print(f"\\nTrying to find a suitable pallet size...")
        
        try:
            return find_best_arrangement_fine_scaling(box, box_count)
        except ValueError as e:
            print(f"\\nCould not find any suitable arrangement: {e}")
            print("\\nSuggestions:")
            print("1. Reduce the number of boxes per layer")
            print(f"2. Use smaller box dimensions (currently {box.width} x {box.length})")
            print("3. Consider using multiple layers or multiple pallets")
            
            # Calculate theoretical maximum for user guidance
            max_boxes_by_area = int(pallet_area_available / box.area)
            print(f"\\nTheoretical maximum boxes by area: {max_boxes_by_area}")
            raise

    return best_arrangement, best_rows, best_columns, standard_pallet


def auto_optimize_box_count(box: Box) -> Tuple[List[List[str]], int, int, int, Pallet]:
    """
    Automatically find the optimal number of boxes per layer.
    
    This advanced feature tests different box counts to find the arrangement that
    maximizes the number of boxes while staying within the original pallet size.
    No scaling is allowed during auto-optimization to ensure compliance with
    standard pallet dimensions.
    
    Args:
        box: Box instance with dimensions
        
    Returns:
        Tuple containing:
        - arrangement: Optimal 2D grid of box orientations
        - rows: Number of rows in optimal arrangement
        - columns: Number of columns in optimal arrangement
        - optimal_box_count: Best number of boxes per layer
        - final_pallet: Pallet instance used (always standard size)
    """
    print("Auto-optimizing number of boxes per layer...")
    
    # Calculate reasonable search range
    single_box_area = box.area
    original_pallet_area = PALLET_WIDTH * PALLET_LENGTH
    theoretical_max = int(original_pallet_area / single_box_area)
    
    print(f"Theoretical maximum boxes by area: {theoretical_max}")
    
    # Initialize tracking variables
    best_arrangement = None
    best_rows = 0
    best_columns = 0
    best_count = 0
    best_pallet = Pallet()
    best_score = float('inf')  # Combined score considering efficiency and area utilization
    
    standard_pallet_area = PALLET_WIDTH * PALLET_LENGTH
    
    # Define search range (start conservative, don't go too high)
    min_boxes = max(1, theoretical_max // 4)  # Start from 25% of theoretical max
    max_boxes = min(theoretical_max * 2, 100)  # Don't go too crazy with box count
    
    print(f"Testing box counts from {min_boxes} to {max_boxes}...")
    
    for box_count in range(min_boxes, max_boxes + 1):
        try:
            # Try both the original algorithm and the flexible algorithm
            arrangement = find_best_arrangement_with_custom_pallet(box, box_count, Pallet())
            
            # Also try the flexible algorithm
            flexible_arrangement = try_flexible_arrangement(box, box_count, Pallet())
            
            # Choose the better arrangement
            best_for_this_count = None
            if arrangement is not None and flexible_arrangement is not None:
                # Both work, choose the one with better area efficiency
                area1 = calculate_arrangement_area(arrangement, box)
                area2 = calculate_arrangement_area(flexible_arrangement, box)
                efficiency1 = min(area1 / standard_pallet_area, standard_pallet_area / area1)
                efficiency2 = min(area2 / standard_pallet_area, standard_pallet_area / area2)
                best_for_this_count = flexible_arrangement if efficiency2 > efficiency1 else arrangement
            elif flexible_arrangement is not None:
                best_for_this_count = flexible_arrangement
            elif arrangement is not None:
                best_for_this_count = arrangement
            
            if best_for_this_count is not None:
                # Found arrangement with original pallet
                rows = len(best_for_this_count)
                columns = len(best_for_this_count[0]) if rows > 0 else 0
                
                # Calculate arrangement area
                from utils.geometry import calculate_arrangement_area
                arrangement_area = calculate_arrangement_area(best_for_this_count, box)
                
                # Calculate area efficiency (how close to using full pallet)
                area_efficiency = min(arrangement_area / standard_pallet_area, 
                                    standard_pallet_area / arrangement_area)
                
                # Calculate box density (boxes per unit area)
                box_density = box_count / arrangement_area
                
                # Combined score: prioritize high area efficiency and high box count
                # Lower score is better
                score = (1.0 - area_efficiency) * 1000 - box_count
                
                print(f"  {box_count} boxes: SUCCESS with original pallet ({rows}x{columns}), area efficiency: {area_efficiency:.3f}, score: {score:.2f}")
                
                if score < best_score:
                    best_arrangement = best_for_this_count
                    best_rows = rows
                    best_columns = columns
                    best_count = box_count
                    best_pallet = Pallet()
                    best_score = score
            else:
                print(f"  {box_count} boxes: FAILED - doesn't fit on original pallet")
        except Exception as e:
            print(f"  {box_count} boxes: ERROR - {e}")
            continue
    
    if best_arrangement is None:
        raise ValueError("Could not find any viable arrangement during auto-optimization")
    
    print(f"\\nOptimal solution: {best_count} boxes per layer")
    print(f"Arrangement: {best_rows} rows x {best_columns} columns")
    
    # Calculate final efficiency for display
    from utils.geometry import calculate_arrangement_area
    final_area = calculate_arrangement_area(best_arrangement, box)
    area_efficiency = min(final_area / standard_pallet_area, standard_pallet_area / final_area)
    print(f"Area efficiency: {area_efficiency:.3f} (closer to 1.0 is better)")
    
    return best_arrangement, best_rows, best_columns, best_count, best_pallet
