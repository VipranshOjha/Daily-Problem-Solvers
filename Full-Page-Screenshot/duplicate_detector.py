"""
duplicate_detector.py

Provides methods to compare screenshots and detect if a scroll action
resulted in the same image (indicating the bottom of the page).
"""
import imagehash
from PIL import Image
from logger import logger

class DuplicateDetector:
    """Detects duplicate images using perceptual hashing."""
    
    def __init__(self, hash_size: int = 8, threshold: int = 1):
        """
        Initializes the detector.
        
        Args:
            hash_size (int): Size of the hash. Larger is more precise.
            threshold (int): Maximum Hamming distance to consider as duplicate.
        """
        self.hash_size = hash_size
        self.threshold = threshold
        
    def get_hash(self, image: Image.Image) -> imagehash.ImageHash:
        """Computes the perceptual hash of an image."""
        try:
            return imagehash.average_hash(image, hash_size=self.hash_size)
        except Exception as e:
            logger.error(f"Failed to compute image hash: {e}")
            raise
            
    def is_duplicate(self, img1: Image.Image, img2: Image.Image) -> bool:
        """
        Compares two images and returns True if they are considered duplicates.
        """
        if img1 is None or img2 is None:
            return False
            
        hash1 = self.get_hash(img1)
        hash2 = self.get_hash(img2)
        
        distance = hash1 - hash2
        logger.debug(f"Image hash distance: {distance}")
        
        return distance <= self.threshold
