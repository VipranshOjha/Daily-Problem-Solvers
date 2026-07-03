import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from workspace_manager import WorkspaceManager

def test_workspace_creation(tmp_path):
    # Override app_data_dir to temp
    wm = WorkspaceManager()
    wm.app_data_dir = tmp_path / "appdata"
    wm.app_data_dir.mkdir(parents=True, exist_ok=True)
    wm.pointer_file = wm.app_data_dir / "workspace_pointer.txt"
    
    # Mock workspace path
    test_workspace = tmp_path / "MyWorkspace"
    wm.workspace_path = test_workspace
    wm._create_structure()
    
    assert (test_workspace / "Output").exists()
    assert (test_workspace / "Logs").exists()
    assert (test_workspace / "Temp").exists()
    assert (test_workspace / "Settings").exists()
    
def test_session_dir_generation(tmp_path):
    wm = WorkspaceManager()
    wm.workspace_path = tmp_path
    
    session_path = wm.get_session_dir("2026-07-01_12-00-00")
    
    assert session_path.exists()
    assert session_path.name == "2026-07-01_12-00-00"
    assert session_path.parent.name == "Output"
