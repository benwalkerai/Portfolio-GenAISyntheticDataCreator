import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir="logs", log_file="app.log", level=logging.INFO):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    file_path = log_path / log_file

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    root_logger.handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=5*1024*1024, 
        backupCount=3, 
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.info(f"Logging initialized. Writing to console and {file_path}")
