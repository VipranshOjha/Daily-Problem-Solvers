"""
page_detector.py

Provides robust detection of static visual states to verify if scrolling has ceased.
"""
import numpy as np
from PIL import Image
from duplicate_detector import DuplicateDetector

class PageDetector:
    """Detects if two screenshots are visually identical (static)."""
    
    def __init__(self):
        self.duplicate_detector = DuplicateDetector()
        
    def _calculate_mse(self, image1: Image.Image, image2: Image.Image) -> float:
        """Calculates Mean Squared Error between two images."""
        try:
            arr1 = np.array(image1.convert('L'), dtype=float)
            arr2 = np.array(image2.convert('L'), dtype=float)
            if arr1.shape != arr2.shape:
                return float('inf')
            err = np.sum((arr1 - arr2) ** 2)
            err /= float(arr1.shape[0] * arr1.shape[1])
            return err
        except Exception:
            return float('inf')
            
    def is_static(self, img_prev: Image.Image, img_curr: Image.Image) -> bool:
        """Determines if the screen has stopped changing (visual staticity)."""
        if not img_prev or not img_curr:
            return False
            
        # 1. Image Hashing (Perceptual match)
        if self.duplicate_detector.is_duplicate(img_prev, img_curr):
            return True
            
        # 2. Pixel MSE (Tolerance for tiny artifacts or blinking cursors)
        mse = self._calculate_mse(img_prev, img_curr)
        if mse < 5.0: # Very tight tolerance
            return True
            
        return False
