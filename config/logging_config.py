"""
Logging configuration for the Synthetic Data Generator.

This module provides a centralized setup for logging, ensuring that logs are
written to both the console and a rotating log file in the 'logs' directory.

Author: Ben Walker (https://github.com/benwalkerai)
Version: 1.0.0
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: str = "logs", log_file: str = "app.log", level: int = logging.INFO) -> None:
    """
    Configure logging to write to both console and a rotating file.
    
    Args:
        log_dir (str): Directory to store log files. Defaults to "logs".
        log_file (str): Name of the log file. Defaults to "app.log".
        level (int): Logging level. Defaults to logging.INFO.
    """
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    file_path = log_path / log_file

    # Create formatters and handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates if called multiple times
    root_logger.handlers = []

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Rotating File Handler
    # Max size 5MB, keep 3 backup files
    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=5*1024*1024, 
        backupCount=3, 
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.info(f"Logging initialized. Writing to console and {file_path}")
