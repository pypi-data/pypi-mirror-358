import os
import sys
import logging
from datetime import datetime

# ANSI escape sequences for colored output
COLORS = {
    logging.DEBUG: "\x1b[36;20m",    # Cyan
    logging.INFO: "\x1b[37;20m",     # White
    logging.WARNING: "\x1b[33;20m",  # Yellow
    logging.ERROR: "\x1b[31;20m",    # Red
    logging.CRITICAL: "\x1b[31;1m",  # Bold Red
}
RESET = "\x1b[0m"

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors and file information to log messages.
    
    Args:
        logging.Formatter: Base formatter class
    """
    def __init__(self):
        fmt = (
            "%(asctime)s | %(levelname)-8s | "
            "%(filename)s:%(lineno)d | "
            "%(message)s"
        )
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.FORMATS = {
            level: f"{color}{self._fmt}{RESET}" 
            for level, color in COLORS.items()
        }

    def format(self, record):
        """Format log messages with color and file information.
        
        Args:
            record: Log record to format
        
        Returns:
            Formatted log message
        """
        log_fmt = self.FORMATS.get(record.levelno, self._fmt)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

def setup_logger(debug_mode=False, log_level=logging.INFO):
    """Set up the logger with file information and colors."""
    # Create logger
    logger = logging.getLogger("pyRNAither")
    logger.setLevel(log_level if not debug_mode else logging.DEBUG)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

    # Optionally add file handler for persistent logging
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(
        log_dir, 
        f"pyRNAither_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(file_handler)

    # Capture warnings
    logging.captureWarnings(True)

    return logger

# Create global logger instance
logger = setup_logger()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler with file information."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error(
        "Uncaught exception:",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

# Install exception handler
sys.excepthook = handle_exception