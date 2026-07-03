"""
logger.py

Provides robust logging capabilities.
"""
import logging
from logging.handlers import RotatingFileHandler
from workspace_manager import workspace_manager

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("Full-Page-Screenshot")
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger
        
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # Global file handler
    logs_dir = workspace_manager.get_logs_dir()
    global_log_file = logs_dir / "app.log"
    fh = RotatingFileHandler(global_log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger

logger = setup_logger()
session_handler = None

def add_session_log(session_dir):
    """Adds a file handler to log directly into the current session folder."""
    global session_handler
    if session_handler:
        logger.removeHandler(session_handler)
        
    log_file = session_dir / "CaptureLog.txt"
    session_handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    session_handler.setFormatter(formatter)
    logger.addHandler(session_handler)
