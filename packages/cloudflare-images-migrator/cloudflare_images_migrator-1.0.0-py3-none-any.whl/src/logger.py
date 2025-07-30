"""
Logging configuration for Cloudflare Images Migration Tool
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style, Back


# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(verbose: bool = False, log_file: str = None) -> logging.Logger:
    """
    Set up the logger with console and file handlers.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Path to log file (optional)
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger('cloudflare_images_migrator')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    console_format = ColoredFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if specified or default)
    if log_file is None:
        log_file = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    try:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        file_format = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
        
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    return logger


class ProgressLogger:
    """Helper class for logging progress with statistics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.stats = {
            'files_processed': 0,
            'images_found': 0,
            'images_uploaded': 0,
            'images_failed': 0,
            'files_modified': 0,
            'errors': []
        }
        self.start_time = datetime.now()
    
    def log_file_processed(self, file_path: str, images_found: int):
        """Log that a file has been processed."""
        self.stats['files_processed'] += 1
        self.stats['images_found'] += images_found
        self.logger.info(f"Processed {file_path}: found {images_found} images")
    
    def log_image_uploaded(self, image_path: str, cloudflare_id: str):
        """Log successful image upload."""
        self.stats['images_uploaded'] += 1
        self.logger.info(f"✓ Uploaded {image_path} -> {cloudflare_id}")
    
    def log_image_failed(self, image_path: str, error: str):
        """Log failed image upload."""
        self.stats['images_failed'] += 1
        self.stats['errors'].append(f"{image_path}: {error}")
        self.logger.error(f"✗ Failed to upload {image_path}: {error}")
    
    def log_file_modified(self, file_path: str, replacements: int):
        """Log file modification."""
        self.stats['files_modified'] += 1
        self.logger.info(f"✓ Modified {file_path}: {replacements} replacements")
    
    def log_progress_summary(self, dry_run: bool = False):
        """Log progress summary."""
        elapsed = datetime.now() - self.start_time
        
        action = "Would modify" if dry_run else "Modified"
        
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"Migration {'Preview' if dry_run else 'Summary'}")
        self.logger.info(f"{'='*50}")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Images found: {self.stats['images_found']}")
        
        if not dry_run:
            self.logger.info(f"Images uploaded: {self.stats['images_uploaded']}")
            self.logger.info(f"Images failed: {self.stats['images_failed']}")
            self.logger.info(f"Files modified: {self.stats['files_modified']}")
        else:
            self.logger.info(f"Images to upload: {self.stats['images_found']}")
            self.logger.info(f"Files to modify: {len(set(self.stats.get('files_to_modify', [])))}")
        
        self.logger.info(f"Time elapsed: {elapsed}")
        
        if self.stats['errors']:
            self.logger.warning(f"\nErrors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                self.logger.warning(f"  - {error}")
            if len(self.stats['errors']) > 10:
                self.logger.warning(f"  ... and {len(self.stats['errors']) - 10} more errors")
        
        self.logger.info(f"{'='*50}")
    
    def get_stats(self) -> dict:
        """Get current statistics."""
        return self.stats.copy() 