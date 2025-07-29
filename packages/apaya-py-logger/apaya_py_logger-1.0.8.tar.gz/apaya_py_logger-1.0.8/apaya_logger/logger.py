"""
Logging configuration for the Apaya Crawler project.

This module provides a centralized logging setup that can be:
1. Configured via environment variables
2. Used across all modules
3. Easily enabled/disabled
4. Output to both console and file with rotation
5. Automatic gzip compression of rotated logs
6. Time-based and size-based rotation
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import gzip
import shutil
from pathlib import Path
from typing import Optional
import glob
import time

# Default logging settings
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_FILE = "apaya_logger.log"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5
DEFAULT_ROTATION_TYPE = "size"  # "size", "time", or "both"
DEFAULT_TIME_INTERVAL = "daily"  # "daily", "weekly", "monthly"
DEFAULT_COMPRESS_AFTER_DAYS = 1  # Compress logs older than 1 day
DEFAULT_DELETE_AFTER_DAYS = 30  # Delete logs older than 30 days (0 = never delete)

class CompressingRotatingFileHandler(RotatingFileHandler):
    """
    Enhanced RotatingFileHandler that compresses rotated log files with gzip.
    """
    
    def __init__(self, *args, compress_after_days=1, delete_after_days=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.compress_after_days = compress_after_days
        self.delete_after_days = delete_after_days
    
    def doRollover(self):
        """
        Do a rollover and compress old log files.
        """
        # Perform the standard rollover
        super().doRollover()
        
        # Compress old log files
        self._compress_old_logs()
        
        # Delete very old log files
        self._delete_old_logs()
    
    def _compress_old_logs(self):
        """
        Compress log files older than compress_after_days.
        """
        try:
            log_dir = Path(self.baseFilename).parent
            log_name = Path(self.baseFilename).stem
            
            # Find all rotated log files
            pattern = f"{log_name}.log.*"
            log_files = glob.glob(str(log_dir / pattern))
            
            current_time = time.time()
            
            for log_file in log_files:
                log_path = Path(log_file)
                
                # Skip if already compressed
                if log_path.suffix == '.gz':
                    continue
                
                # Check if file is old enough to compress
                file_age_days = (current_time - log_path.stat().st_mtime) / (24 * 3600)
                
                if file_age_days >= self.compress_after_days:
                    self._compress_file(log_path)
        
        except Exception as e:
            # Don't let compression errors break logging
            print(f"Warning: Failed to compress log files: {e}")
    
    def _compress_file(self, file_path: Path):
        """
        Compress a single log file with gzip.
        """
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file after successful compression
            file_path.unlink()
            print(f"Compressed log file: {file_path} -> {compressed_path}")
            
        except Exception as e:
            print(f"Warning: Failed to compress {file_path}: {e}")
    
    def _delete_old_logs(self):
        """
        Delete log files older than delete_after_days.
        """
        if self.delete_after_days <= 0:
            return  # Deletion disabled
            
        try:
            log_dir = Path(self.baseFilename).parent
            log_name = Path(self.baseFilename).stem
            
            # Find all log files (compressed and uncompressed)
            patterns = [f"{log_name}.log.*", f"{log_name}.log.*.gz"]
            log_files = []
            for pattern in patterns:
                log_files.extend(glob.glob(str(log_dir / pattern)))
            
            current_time = time.time()
            deleted_count = 0
            
            for log_file in log_files:
                log_path = Path(log_file)
                
                # Check if file is old enough to delete
                file_age_days = (current_time - log_path.stat().st_mtime) / (24 * 3600)
                
                if file_age_days >= self.delete_after_days:
                    try:
                        log_path.unlink()
                        deleted_count += 1
                        print(f"Deleted old log file: {log_path}")
                    except Exception as e:
                        print(f"Warning: Failed to delete {log_path}: {e}")
            
            if deleted_count > 0:
                print(f"Deleted {deleted_count} old log files (older than {self.delete_after_days} days)")
        
        except Exception as e:
            # Don't let deletion errors break logging
            print(f"Warning: Failed to delete old log files: {e}")

class CompressingTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Enhanced TimedRotatingFileHandler that compresses rotated log files with gzip.
    """
    
    def __init__(self, *args, compress_after_days=1, delete_after_days=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.compress_after_days = compress_after_days
        self.delete_after_days = delete_after_days
    
    def doRollover(self):
        """
        Do a rollover and compress old log files.
        """
        # Perform the standard rollover
        super().doRollover()
        
        # Compress old log files
        self._compress_old_logs()
        
        # Delete very old log files
        self._delete_old_logs()
    
    def _compress_old_logs(self):
        """
        Compress log files older than compress_after_days.
        """
        try:
            log_dir = Path(self.baseFilename).parent
            log_name = Path(self.baseFilename).name
            
            # Find all rotated log files (TimedRotatingFileHandler uses different naming)
            pattern = f"{log_name}.*"
            log_files = glob.glob(str(log_dir / pattern))
            
            current_time = time.time()
            
            for log_file in log_files:
                log_path = Path(log_file)
                
                # Skip current log file and already compressed files
                if log_path.name == log_name or log_path.suffix == '.gz':
                    continue
                
                # Check if file is old enough to compress
                file_age_days = (current_time - log_path.stat().st_mtime) / (24 * 3600)
                
                if file_age_days >= self.compress_after_days:
                    self._compress_file(log_path)
        
        except Exception as e:
            # Don't let compression errors break logging
            print(f"Warning: Failed to compress log files: {e}")
    
    def _compress_file(self, file_path: Path):
        """
        Compress a single log file with gzip.
        """
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file after successful compression
            file_path.unlink()
            print(f"Compressed log file: {file_path} -> {compressed_path}")
            
        except Exception as e:
            print(f"Warning: Failed to compress {file_path}: {e}")
    
    def _delete_old_logs(self):
        """
        Delete log files older than delete_after_days.
        """
        if self.delete_after_days <= 0:
            return  # Deletion disabled
            
        try:
            log_dir = Path(self.baseFilename).parent
            log_name = Path(self.baseFilename).name
            
            # Find all log files (compressed and uncompressed)
            # TimedRotatingFileHandler uses different naming pattern
            patterns = [f"{log_name}.*", f"{log_name}.*.gz"]
            log_files = []
            for pattern in patterns:
                log_files.extend(glob.glob(str(log_dir / pattern)))
            
            current_time = time.time()
            deleted_count = 0
            
            for log_file in log_files:
                log_path = Path(log_file)
                
                # Skip current log file
                if log_path.name == log_name:
                    continue
                
                # Check if file is old enough to delete
                file_age_days = (current_time - log_path.stat().st_mtime) / (24 * 3600)
                
                if file_age_days >= self.delete_after_days:
                    try:
                        log_path.unlink()
                        deleted_count += 1
                        print(f"Deleted old log file: {log_path}")
                    except Exception as e:
                        print(f"Warning: Failed to delete {log_path}: {e}")
            
            if deleted_count > 0:
                print(f"Deleted {deleted_count} old log files (older than {self.delete_after_days} days)")
        
        except Exception as e:
            # Don't let deletion errors break logging
            print(f"Warning: Failed to delete old log files: {e}")

class ApayaLogger:
    """Custom logger for Apaya Crawler with configurable settings and compression."""

    def __init__(
        self,
        name: str,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        log_format: Optional[str] = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None,
        rotation_type: Optional[str] = None,
        time_interval: Optional[str] = None,
        compress_after_days: Optional[int] = None,
        delete_after_days: Optional[int] = None
    ):
        """
        Initialize the logger with custom settings.
        
        Args:
            name: Name of the logger (usually __name__)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file
            log_format: Format string for log messages
            log_to_console: Whether to log to console
            log_to_file: Whether to log to file
            max_bytes: Maximum size of log file before rotation (size-based)
            backup_count: Number of backup files to keep
            rotation_type: Type of rotation ("size", "time", or "both")
            time_interval: Time interval for rotation ("daily", "weekly", "monthly")
            compress_after_days: Compress logs older than this many days
            delete_after_days: Delete logs older than this many days (0 = never delete)
        """
        # Get settings from environment or use defaults
        self.log_level = os.getenv("APAYA_LOG_LEVEL", log_level or DEFAULT_LOG_LEVEL)
        self.log_file = os.getenv("APAYA_LOG_FILE", log_file or DEFAULT_LOG_FILE)
        self.log_format = os.getenv("APAYA_LOG_FORMAT", log_format or DEFAULT_LOG_FORMAT)
        self.log_to_console = os.getenv("APAYA_LOG_TO_CONSOLE", str(log_to_console)).lower() == "true"
        self.log_to_file = os.getenv("APAYA_LOG_TO_FILE", str(log_to_file)).lower() == "true"
        self.max_bytes = int(os.getenv("APAYA_LOG_MAX_BYTES", max_bytes or DEFAULT_MAX_BYTES))
        self.backup_count = int(os.getenv("APAYA_LOG_BACKUP_COUNT", backup_count or DEFAULT_BACKUP_COUNT))
        self.rotation_type = os.getenv("APAYA_LOG_ROTATION_TYPE", rotation_type or DEFAULT_ROTATION_TYPE)
        self.time_interval = os.getenv("APAYA_LOG_TIME_INTERVAL", time_interval or DEFAULT_TIME_INTERVAL)
        self.compress_after_days = int(os.getenv("APAYA_LOG_COMPRESS_AFTER_DAYS", compress_after_days or DEFAULT_COMPRESS_AFTER_DAYS))
        self.delete_after_days = int(os.getenv("APAYA_LOG_DELETE_AFTER_DAYS", delete_after_days or DEFAULT_DELETE_AFTER_DAYS))

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.log_level.upper()))

        # Remove any existing handlers to avoid duplicates
        self.logger.handlers = []

        # Create formatter
        formatter = logging.Formatter(self.log_format)

        # Add console handler if enabled
        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Add file handler if enabled
        if self.log_to_file:
            # Create logs directory if it doesn't exist
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_path = log_dir / self.log_file
            
            # Choose rotation strategy
            if self.rotation_type == "time":
                file_handler = self._create_time_based_handler(log_path, formatter)
            elif self.rotation_type == "both":
                # For "both", we'll use time-based as primary and size as backup
                file_handler = self._create_time_based_handler(log_path, formatter)
            else:  # Default to size-based
                file_handler = self._create_size_based_handler(log_path, formatter)
            
            self.logger.addHandler(file_handler)
            
            # Log the configuration
            self.logger.info(f"Logging initialized - Type: {self.rotation_type}, "
                           f"Max size: {self.max_bytes/1024/1024:.1f}MB, "
                           f"Backup count: {self.backup_count}, "
                           f"Time interval: {self.time_interval}, "
                           f"Compress after: {self.compress_after_days} days, "
                           f"Delete after: {self.delete_after_days} days")

    def _create_size_based_handler(self, log_path: Path, formatter):
        """Create a size-based rotating file handler with compression."""
        file_handler = CompressingRotatingFileHandler(
            log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8',
            compress_after_days=self.compress_after_days,
            delete_after_days=self.delete_after_days
        )
        file_handler.setFormatter(formatter)
        return file_handler

    def _create_time_based_handler(self, log_path: Path, formatter):
        """Create a time-based rotating file handler with compression."""
        # Map time intervals to TimedRotatingFileHandler parameters
        interval_map = {
            "daily": ("D", 1),
            "weekly": ("W0", 1),  # W0 = Monday
            "monthly": ("M", 1)
        }
        
        when, interval = interval_map.get(self.time_interval, ("D", 1))
        
        file_handler = CompressingTimedRotatingFileHandler(
            log_path,
            when=when,
            interval=interval,
            backupCount=self.backup_count,
            encoding='utf-8',
            compress_after_days=self.compress_after_days,
            delete_after_days=self.delete_after_days
        )
        file_handler.setFormatter(formatter)
        return file_handler

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(msg, *args, **kwargs)

# Create a default logger instance
logger = ApayaLogger(__name__)

# Example usage:
# from app.utils.logging import ApayaLogger
# logger = ApayaLogger(__name__)
# logger.info("Starting content generation...")
# logger.error("Failed to generate content", exc_info=True) 