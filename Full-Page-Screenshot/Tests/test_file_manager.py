import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from file_manager import FileManager

def test_clean_filename():
    fm = FileManager()
    
    assert fm.clean_filename("Google - Google Chrome") == "Google - Google Chrome"
    assert fm.clean_filename("Title with <illegal> chars?") == "Title with _illegal_ chars_"
    assert fm.clean_filename("   Trailing spaces   ") == "Trailing spaces"
    assert fm.clean_filename("") == "Untitled_Page"
    
    long_title = "A" * 200
    assert len(fm.clean_filename(long_title)) == 150
