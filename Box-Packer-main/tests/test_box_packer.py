"""
Unit tests for the Box Packer application.

This module contains comprehensive tests for all major components.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Box, Pallet
from utils.geometry import calculate_arrangement_area, arrangement_fits_in_pallet, ratio_score
from algorithms.arrangement import generate_candidates, try_arrangement
from config import PALLET_WIDTH, PALLET_LENGTH, TARGET_RATIO


class TestBox(unittest.TestCase):
    """Test the Box class."""
    
    def test_box_creation(self):
        """Test basic box creation."""
        box = Box(10, 20)
        self.assertEqual(box.width, 10)
        self.assertEqual(box.length, 20)
        self.assertEqual(box.area, 200)
    
    def test_box_dimension_swapping(self):
        """Test that box dimensions are swapped when width > length."""
        # This should swap dimensions automatically
        box = Box(20, 10)
        self.assertEqual(box.width, 10)
        self.assertEqual(box.length, 20)
    
    def test_box_validation(self):
        """Test box validation for invalid dimensions."""
        with self.assertRaises(ValueError):
            Box(0, 10)  # Zero width
        with self.assertRaises(ValueError):
            Box(10, -5)  # Negative length
    
    def test_box_orientations(self):
        """Test box orientation calculations."""
        box = Box(10, 20)
        
        # Normal orientation
        width, height = box.get_dimensions_for_orientation('N')
        self.assertEqual(width, 10)
        self.assertEqual(height, 20)
        
        # Rotated orientation
        width, height = box.get_dimensions_for_orientation('R')
        self.assertEqual(width, 20)
        self.assertEqual(height, 10)
        
        # Invalid orientation
        with self.assertRaises(ValueError):
            box.get_dimensions_for_orientation('X')
    
    def test_box_fit_in_space(self):
        """Test if box can fit in given space."""
        box = Box(10, 20)
        
        # Should fit in both orientations
        self.assertTrue(box.can_fit_in_space(25, 25))
        
        # Should fit only in rotated orientation
        self.assertTrue(box.can_fit_in_space(25, 15))
        
        # Should not fit in either orientation
        self.assertFalse(box.can_fit_in_space(8, 8))
    
    def test_box_best_orientation(self):
        """Test best orientation selection."""
        box = Box(10, 20)
        
        # Should choose normal orientation for tall spaces
        self.assertEqual(box.best_orientation_for_space(15, 25), 'N')
        
        # Should choose rotated orientation for wide spaces
        self.assertEqual(box.best_orientation_for_space(25, 15), 'R')
        
        # Should raise error if doesn't fit
        with self.assertRaises(ValueError):
            box.best_orientation_for_space(8, 8)


class TestPallet(unittest.TestCase):
    """Test the Pallet class."""
    
    def test_pallet_creation(self):
        """Test basic pallet creation."""
        pallet = Pallet()
        self.assertEqual(pallet.width, PALLET_WIDTH)
        self.assertEqual(pallet.length, PALLET_LENGTH)
        self.assertEqual(pallet.area, PALLET_WIDTH * PALLET_LENGTH)
    
    def test_custom_pallet(self):
        """Test custom pallet dimensions."""
        pallet = Pallet(50, 60)
        self.assertEqual(pallet.width, 50)
        self.assertEqual(pallet.length, 60)
        self.assertEqual(pallet.area, 3000)
    
    def test_pallet_scaling(self):
        """Test pallet scaling."""
        pallet = Pallet()
        scaled = pallet.scale(2.0)
        self.assertEqual(scaled.width, PALLET_WIDTH * 2)
        self.assertEqual(scaled.length, PALLET_LENGTH * 2)
    
    def test_standard_size_check(self):
        """Test standard size detection."""
        standard_pallet = Pallet()
        self.assertTrue(standard_pallet.is_standard_size)
        
        custom_pallet = Pallet(50, 60)
        self.assertFalse(custom_pallet.is_standard_size)


class TestGeometry(unittest.TestCase):
    """Test geometric utility functions."""
    
    def test_ratio_score(self):
        """Test ratio score calculation."""
        # Perfect ratio should have score 0
        ideal_ratio = TARGET_RATIO
        rows = int(ideal_ratio * 5)
        score = ratio_score(rows, 5)
        self.assertAlmostEqual(score, 0, places=6)
        
        # Non-ideal ratio should have positive score
        score = ratio_score(10, 5)
        self.assertGreater(score, 0)
    
    def test_arrangement_area_calculation(self):
        """Test arrangement area calculation."""
        box = Box(10, 20)
        
        # Simple 2x2 arrangement with all normal orientations
        arrangement = [['N', 'N'], ['N', 'N']]
        area = calculate_arrangement_area(arrangement, box)
        
        # Each column should be 10 wide, 40 high (2 boxes * 20 each)
        # Total: 20 wide, 40 high = 800 area
        self.assertEqual(area, 800)
    
    def test_arrangement_fits_in_pallet(self):
        """Test arrangement fit checking."""
        box = Box(10, 20)
        pallet = Pallet(50, 50)
        
        # Small arrangement should fit
        arrangement = [['N', 'N']]
        self.assertTrue(arrangement_fits_in_pallet(arrangement, box, pallet))
        
        # Large arrangement should not fit
        arrangement = [['N'] * 10] * 10  # 100 boxes
        self.assertFalse(arrangement_fits_in_pallet(arrangement, box, pallet))


class TestArrangement(unittest.TestCase):
    """Test arrangement generation algorithms."""
    
    def test_generate_candidates(self):
        """Test candidate generation."""
        # Test with 6 boxes
        candidates = generate_candidates(6)
        
        # Should include (6,1), (3,2), (2,3) but not (1,6) due to rows >= columns constraint
        valid_candidates = [(6, 1), (3, 2), (2, 3)]
        
        # Check that all valid candidates are present
        for candidate in valid_candidates:
            self.assertIn(candidate, candidates)
        
        # Check that invalid candidates are not present
        self.assertNotIn((1, 6), candidates)
    
    def test_try_arrangement(self):
        """Test arrangement trying."""
        box = Box(10, 20)
        pallet = Pallet(50, 50)
        
        # Should be able to arrange 4 boxes in 2x2
        arrangement = try_arrangement(2, 2, box, 4, pallet)
        self.assertIsNotNone(arrangement)
        
        # Should not be able to arrange 100 boxes in 10x10 on standard pallet
        arrangement = try_arrangement(10, 10, box, 100, pallet)
        self.assertIsNone(arrangement)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def test_small_box_arrangement(self):
        """Test arranging small boxes."""
        box = Box(5, 8)
        pallet = Pallet()
        
        # Should be able to fit many small boxes
        arrangement = try_arrangement(5, 4, box, 20, pallet)
        self.assertIsNotNone(arrangement)
        
        # Verify arrangement fits
        self.assertTrue(arrangement_fits_in_pallet(arrangement, box, pallet))
    
    def test_large_box_arrangement(self):
        """Test arranging large boxes."""
        box = Box(15, 30)
        pallet = Pallet()
        
        # Should be able to fit fewer large boxes
        arrangement = try_arrangement(2, 1, box, 2, pallet)
        self.assertIsNotNone(arrangement)
        
        # Verify arrangement fits
        self.assertTrue(arrangement_fits_in_pallet(arrangement, box, pallet))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
