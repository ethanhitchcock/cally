"""Debug logging module for calcure"""

import logging
import datetime
from pathlib import Path

class DebugLogger:
    """Enhanced debug logger for calcure"""
    
    def __init__(self, log_file=None):
        # Default to calcure directory if not specified
        if log_file is None:
            # Try to find calcure directory
            import os
            calcure_dir = Path(__file__).parent.parent if Path(__file__).parent.name == 'calcure' else Path.cwd()
            self.log_file = calcure_dir / "calcure_debug.log"
        else:
            self.log_file = Path(log_file)
        self.logger = logging.getLogger('calcure_debug')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler
        fh = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        self.logger.info("=" * 80)
        self.logger.info("Calcure Debug Log Started")
        self.logger.info("=" * 80)
    
    def log_data_load(self, loader_name, item_count, details=None):
        """Log data loading information"""
        self.logger.info(f"[DATA LOAD] {loader_name}: Loaded {item_count} items")
        if details:
            self.logger.debug(f"  Details: {details}")
    
    def log_error(self, error_type, message, exception=None):
        """Log errors"""
        self.logger.error(f"[ERROR] {error_type}: {message}")
        if exception:
            self.logger.exception(exception)
    
    def log_warning(self, warning_type, message):
        """Log warnings"""
        self.logger.warning(f"[WARNING] {warning_type}: {message}")
    
    def log_event(self, event_type, message):
        """Log events"""
        self.logger.info(f"[EVENT] {event_type}: {message}")
    
    def log_crash(self, exception, traceback_str=None):
        """Log crash information"""
        self.logger.critical("=" * 80)
        self.logger.critical("CRASH DETECTED")
        self.logger.critical("=" * 80)
        self.logger.critical(f"Exception: {type(exception).__name__}: {str(exception)}")
        if traceback_str:
            self.logger.critical(f"Traceback:\n{traceback_str}")
        self.logger.critical("=" * 80)

# Global debug logger instance
debug_logger = None

def init_debug_logger(log_file="calcure_debug.log"):
    """Initialize the global debug logger"""
    global debug_logger
    debug_logger = DebugLogger(log_file)
    return debug_logger

def get_debug_logger():
    """Get the global debug logger"""
    global debug_logger
    if debug_logger is None:
        debug_logger = init_debug_logger()
    return debug_logger

