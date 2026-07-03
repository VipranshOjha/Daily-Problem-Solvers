import pytest
import sys
import os
from PIL import Image
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from export_pipeline import ExportPipeline
from config import config_manager

def test_export_pipeline_png(tmp_path):
    config_manager.settings.export_format = "PNG"
    exporter = ExportPipeline()
    
    img = Image.new('RGB', (100, 100), color = 'red')
    output_path = tmp_path / "test.png"
    
    exporter.export(img, output_path, "Test")
    
    assert output_path.exists()
    assert output_path.suffix == ".png"

def test_export_pipeline_pdf(tmp_path):
    config_manager.settings.export_format = "PDF"
    config_manager.settings.pdf_page_size = "A4"
    config_manager.settings.pdf_orientation = "Portrait"
    config_manager.settings.pdf_dpi = 150
    exporter = ExportPipeline()
    
    # Create a very tall image
    img = Image.new('RGB', (1000, 3000), color = 'blue')
    output_path = tmp_path / "test.pdf"
    
    exporter.export(img, output_path, "Test Document")
    
    assert output_path.exists()
    assert output_path.suffix == ".pdf"
