"""
workspace_manager.py

Handles the First Run Wizard and sets up the root Workspace folder.
Ensures session isolation.
"""
import os
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

class WorkspaceManager:
    """Manages the application's root workspace."""
    
    def __init__(self):
        self.app_data_dir = Path.home() / "AppData" / "Local" / "Full-Page-Screenshot"
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        self.pointer_file = self.app_data_dir / "workspace_pointer.txt"
        self.workspace_path = None
        
    def setup_workspace(self) -> Path:
        """Locates the workspace, running the First Run Wizard if needed."""
        if self.pointer_file.exists():
            saved_path = self.pointer_file.read_text().strip()
            if os.path.exists(saved_path):
                self.workspace_path = Path(saved_path)
                self._create_structure()
                return self.workspace_path
                
        # Run wizard if not found
        self._run_first_time_wizard()
        self._create_structure()
        return self.workspace_path
        
    def _run_first_time_wizard(self):
        root = tk.Tk()
        root.withdraw()
        
        documents_folder = Path.home() / "Documents"
        default_workspace = documents_folder / "Full-Page-Screenshot"
        
        msg = (
            "Welcome to Full-Page-Screenshot!\n\n"
            "We need to set up a Workspace folder where all your PDFs and logs will be saved.\n"
            f"The default is:\n{default_workspace}\n\n"
            "Would you like to use the default location? (Click No to choose a custom folder)"
        )
        
        use_default = messagebox.askyesno("Workspace Setup", msg)
        
        if use_default:
            self.workspace_path = default_workspace
        else:
            messagebox.showinfo("Select Workspace", "Please select an empty folder to use as your Workspace root.")
            selected = filedialog.askdirectory(title="Select Workspace Folder")
            if selected:
                self.workspace_path = Path(selected) / "Full-Page-Screenshot"
            else:
                self.workspace_path = default_workspace
                
        # Save pointer
        self.pointer_file.write_text(str(self.workspace_path))
        root.destroy()
        
    def _create_structure(self):
        """Ensures all required subdirectories exist."""
        folders = ["Output", "Logs", "Temp", "Settings", "Assets"]
        for f in folders:
            (self.workspace_path / f).mkdir(parents=True, exist_ok=True)
            
    def get_settings_file(self) -> Path:
        return self.workspace_path / "Settings" / "settings.json"
        
    def get_session_dir(self, session_id: str) -> Path:
        """Returns a path for a specific session inside Output."""
        session_path = self.workspace_path / "Output" / session_id
        session_path.mkdir(parents=True, exist_ok=True)
        return session_path
        
    def get_temp_dir(self) -> Path:
        return self.workspace_path / "Temp"
        
    def get_logs_dir(self) -> Path:
        return self.workspace_path / "Logs"

# Global workspace manager
workspace_manager = WorkspaceManager()
