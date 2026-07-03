import pytest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import ConfigManager
from settings import Settings

def test_config_load_defaults(tmp_path):
    # Pass a non-existent file path
    config_file = tmp_path / "config.json"
    manager = ConfigManager(config_path=config_file)
    
    assert manager.settings.scroll_speed == Settings().scroll_speed
    assert manager.settings.image_format == "PNG"

def test_config_save_and_load(tmp_path):
    config_file = tmp_path / "config.json"
    manager1 = ConfigManager(config_path=config_file)
    manager1.settings.scroll_speed = 9.9
    manager1.save()
    
    assert config_file.exists()
    
    manager2 = ConfigManager(config_path=config_file)
    assert manager2.settings.scroll_speed == 9.9
