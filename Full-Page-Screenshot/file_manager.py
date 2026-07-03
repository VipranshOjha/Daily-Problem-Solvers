"""
file_manager.py

Handles file naming, path sanitation, and temporary image cleanup.
"""
import re
import os
import json
from datetime import datetime
from pathlib import Path
from logger import logger
from config import config_manager
from workspace_manager import workspace_manager

class FileManager:
    """Manages files, output folders, session data, and temp cleanup."""
    
    def __init__(self):
        self.config = config_manager.settings
        self.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = workspace_manager.get_session_dir(self.session_id)
        
        # Temp dir is still global
        self.temp_dir = workspace_manager.get_temp_dir()
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_filename(self, title: str, max_length: int = 150) -> str:
        """
        Cleans a string to be a valid filename.
        Removes illegal characters and truncates to max_length.
        """
        # Remove illegal characters for Windows/Linux
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', title)
        # Remove leading/trailing spaces and dots
        cleaned = cleaned.strip('. ')
        
        if not cleaned:
            cleaned = "Untitled_Page"
            
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length].strip('. ')
            
        return cleaned
        
    def generate_filename(self, index: int, title: str) -> Path:
        """Generates a unique filename for the stitched output."""
        safe_title = self.clean_filename(title)
        ext = self.config.export_format.lower()
        if ext == "jpeg":
            ext = "jpg"
            
        filename = f"{index:03d}_{safe_title}.{ext}"
        output_path = self.session_dir / filename
        
        return output_path

    def save_session_data(self, data: dict):
        """Saves session metadata to Session.json in the session folder."""
        session_file = self.session_dir / "Session.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved session data to {session_file}")
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")
            
    def get_temp_path(self, suffix: str = ".png") -> Path:
        """Returns a path for a temporary file."""
        return self.temp_dir / f"temp_{os.urandom(4).hex()}{suffix}"
        
    def clear_temp_dir(self):
        """Deletes all files in the temporary directory."""
        logger.debug("Clearing temporary directory...")
        for file in self.temp_dir.iterdir():
            try:
                if file.is_file():
                    file.unlink()
            except Exception as e:
                logger.error(f"Failed to clean up temp files: {e}")
