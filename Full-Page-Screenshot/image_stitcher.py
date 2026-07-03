"""
image_stitcher.py

Stitches multiple screenshots together into a single long PNG.
Handles overlap removal and memory efficiency.
"""
import cv2
import numpy as np
from PIL import Image
from logger import logger
from exceptions import StitchingError
from config import config_manager

# Support images over 100,000 pixels tall
Image.MAX_IMAGE_PIXELS = None

class ImageStitcher:
    """Stitches multiple screenshots into a single continuous image."""
    
    def __init__(self):
        self.config = config_manager.settings

    def stitch_images(self, images: list[Image.Image]) -> Image.Image:
        """
        Stitches a list of PIL Images vertically.
        
        Args:
            images: List of PIL Images to stitch.
            
        Returns:
            PIL.Image.Image: The final stitched image.
        """
        if not images:
            logger.warning("No images provided for stitching.")
            return None
            
        logger.info(f"Stitching {len(images)} images...")
        
        try:
            widths, heights = zip(*(i.size for i in images))
            max_width = max(widths)
            
            overlap = self.config.overlap
            
            # Total height = sum of all heights - overlaps (except for first image)
            total_height = sum(heights) - (overlap * (len(images) - 1))
            
            # Create a new blank image
            stitched_image = Image.new('RGB', (max_width, total_height))
            
            y_offset = 0
            for i, img in enumerate(images):
                if i == 0:
                    stitched_image.paste(img, (0, y_offset))
                    y_offset += img.size[1]
                else:
                    # Crop the overlap from the top of the current image
                    crop_img = img.crop((0, overlap, img.size[0], img.size[1]))
                    stitched_image.paste(crop_img, (0, y_offset))
                    y_offset += crop_img.size[1]
                
            return stitched_image
            
        except Exception as e:
            logger.error(f"Failed to stitch images: {e}")
            raise StitchingError(f"Failed to stitch images: {e}")
