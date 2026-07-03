"""
ocr_utils.py

Provides OCR capabilities to assist in bottom detection.
Requires Tesseract-OCR to be installed on the system.
"""
import pytesseract
from PIL import Image
from logger import logger

def extract_text(image: Image.Image) -> str:
    """
    Extracts text from a PIL image using pytesseract.
    
    Args:
        image: The image to process.
        
    Returns:
        Extracted text as a string. Returns empty string on failure.
    """
    try:
        # Convert to grayscale to improve OCR speed/accuracy
        gray_image = image.convert('L')
        text = pytesseract.image_to_string(gray_image)
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR text extraction failed (is Tesseract installed?): {e}")
        return ""
        
def compare_text(text1: str, text2: str) -> bool:
    """
    Compares two extracted text strings.
    Returns True if they are functionally identical (meaning same content).
    """
    if not text1 and not text2:
        return False # If both are empty, don't rely on OCR for duplicate detection
    return text1 == text2
