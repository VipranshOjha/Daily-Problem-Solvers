"""
config.py

Handles loading, saving, and providing access to application configuration.
"""
import json
import os
import logging
from pathlib import Path
from settings import Settings
from workspace_manager import workspace_manager

class ConfigManager:
    """Manages application configuration, persisting via JSON."""
    
    def __init__(self):
        # Trigger First Run Wizard if needed
        self.workspace_path = workspace_manager.setup_workspace()
        self.config_file = workspace_manager.get_settings_file()
        self.settings = Settings()
        self.load()
        
    def load(self) -> None:
        """Loads configuration from JSON file."""
        if not self.config_file.exists():
            self.save() # generate default
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for key, value in data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
                    
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_file}: {e}")
            
    def save(self) -> None:
        """Saves current configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=4)
        except Exception as e:
            print(f"Warning: Failed to save config to {self.config_file}: {e}")

# Global singleton
config_manager = ConfigManager()
