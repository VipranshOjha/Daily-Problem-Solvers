"""
export_pipeline.py

Handles exporting the stitched image into the desired format (PDF, PNG, JPEG).
Supports splitting long images into multi-page PDFs.
"""
from PIL import Image
from pathlib import Path
from datetime import datetime
from config import config_manager
from logger import logger

class ExportPipeline:
    """Manages the final export of screenshots to various formats."""
    
    def __init__(self):
        self.config = config_manager.settings
        
    def export(self, image: Image.Image, output_path: Path, title: str) -> None:
        """Exports the image based on configured format."""
        if image is None:
            return
            
        format_type = self.config.export_format.upper()
        
        try:
            if format_type == "PDF":
                self._export_to_pdf(image, output_path, title)
            elif format_type in ("JPEG", "JPG"):
                # Convert to RGB to remove alpha channel for JPEG
                if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                    bg = Image.new('RGB', image.size, (255, 255, 255))
                    # Handle masks properly depending on PIL version
                    try:
                        bg.paste(image, mask=image.split()[3])
                    except:
                        bg.paste(image)
                    image = bg
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                    
                image.save(output_path, "JPEG", quality=95)
                logger.info(f"Successfully saved JPEG to {output_path}")
            else:
                # Default to PNG
                image.save(output_path, "PNG", compress_level=self.config.compression)
                logger.info(f"Successfully saved PNG to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export image: {e}")
            raise
            
    def _export_to_pdf(self, image: Image.Image, output_path: Path, title: str) -> None:
        """Exports image to PDF with pagination if necessary."""
        dpi = self.config.pdf_dpi
        page_size_str = self.config.pdf_page_size
        orientation = self.config.pdf_orientation
        
        # Dimensions in inches
        width_in, height_in = 8.27, 11.69 # A4 default
        
        if page_size_str == "Letter":
            width_in, height_in = 8.5, 11.0
            
        if orientation == "Landscape":
            width_in, height_in = height_in, width_in
            
        # We need to preserve aspect ratio. 
        img_width, img_height = image.size
        
        # Calculate target width in pixels based on DPI
        target_width_px = int(width_in * dpi)
        
        # Calculate scaling factor
        scale = target_width_px / float(img_width)
        scaled_height_px = int(img_height * scale)
        
        # Resize image for PDF
        if scale != 1.0:
            logger.debug(f"Rescaling image for PDF from {img_width} to {target_width_px} width (DPI: {dpi})")
            # Use Resampling.LANCZOS for high quality
            image = image.resize((target_width_px, scaled_height_px), Image.Resampling.LANCZOS)
            
        target_height_px = int(height_in * dpi)
        
        pages = []
        if page_size_str == "Auto Height":
            # Single page, auto height
            if image.mode != 'RGB':
                image = image.convert('RGB')
            pages.append(image)
        else:
            # Multi-page splitting
            y_offset = 0
            while y_offset < scaled_height_px:
                crop_height = min(target_height_px, scaled_height_px - y_offset)
                crop_img = image.crop((0, y_offset, target_width_px, y_offset + crop_height))
                
                # If it's the last page and shorter than full height, pad it with white
                if crop_height < target_height_px:
                    padded = Image.new('RGB', (target_width_px, target_height_px), (255, 255, 255))
                    padded.paste(crop_img, (0, 0))
                    crop_img = padded
                    
                if crop_img.mode != 'RGB':
                    crop_img = crop_img.convert('RGB')
                    
                pages.append(crop_img)
                y_offset += crop_height
                
        # Generate Metadata (Pillow supports some basic metadata for PDF)
        # Pillow save allows 'title' and 'author' kwargs
        
        # Save as PDF
        if pages:
            first_page = pages[0]
            if len(pages) > 1:
                first_page.save(
                    output_path, "PDF", resolution=dpi, save_all=True, append_images=pages[1:],
                    title=title, author="Full-Page-Screenshot"
                )
            else:
                first_page.save(output_path, "PDF", resolution=dpi, title=title, author="Full-Page-Screenshot")
                
            logger.info(f"Successfully saved {len(pages)}-page PDF to {output_path}")
