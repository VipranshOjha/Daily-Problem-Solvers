import pytest
import sys
from PIL import Image
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from duplicate_detector import DuplicateDetector

def test_is_duplicate():
    detector = DuplicateDetector(threshold=2)
    
    # Create two identical blank images
    img1 = Image.new('RGB', (100, 100), color = 'red')
    img2 = Image.new('RGB', (100, 100), color = 'red')
    
    assert detector.is_duplicate(img1, img2) == True
    
    # Create a different image
    img3 = Image.new('RGB', (100, 100), color = 'blue')
    
    assert detector.is_duplicate(img1, img3) == False
