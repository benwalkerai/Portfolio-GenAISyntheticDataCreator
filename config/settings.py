"""
Configuration settings for the Synthetic Data Generator.

This module contains all configuration settings, file format definitions,
and constants used throughout the synthetic data generation system.
It provides a centralized location for managing application settings
and ensures consistent behavior across different components.

Author: Ben Walker (https://github.com/benwalkerai)
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Union

# Try to import reportlab, with fallback
try:
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE: bool = True
except ImportError:
    REPORTLAB_AVAILABLE: bool = False

# Type alias for file format configuration structure
FileFormatConfig = Dict[str, Union[str, int, bool, List[str]]]

# Updated file format configurations with text inputs instead of dropdowns
file_format_options: Dict[str, FileFormatConfig] = {
    # Word Document configuration
    # Supports various document types with page-based sizing
    "Word Document (.docx)": {
        "formats": ["Word Document (.docx)"],  # Supported file extensions
        "size_type": "pages",  # Measurement unit for document size
        "size_label": "Number of Pages (1-50)",  # UI label for size input
        "size_default": 4,  # Default number of pages
        "size_max": 50,  # Maximum allowed pages
        "content_options": ["whitepaper", "article", "report", "proposal", "design"],  # Available content types
        "content_label": "Document Type",  # UI label for content selection
        "uses_dropdowns": True  # Documents still use dropdowns for content type
    },
    
    # Plain text file configuration
    # Similar to Word but outputs plain text format
    "Text File (.txt)": {
        "formats": ["Text File (.txt)"],  # Supported file extensions
        "size_type": "pages",  # Measurement unit for document size
        "size_label": "Number of Pages (1-50)",  # UI label for size input
        "size_default": 4,  # Default number of pages
        "size_max": 50,  # Maximum allowed pages
        "content_options": ["whitepaper", "article", "report", "proposal", "design"],  # Available content types
        "content_label": "Document Type",  # UI label for content selection
        "uses_dropdowns": True  # Documents still use dropdowns for content type
    },
    
    # Excel spreadsheet configuration
    # Uses row/column based sizing instead of pages
    "Excel Spreadsheet (.xlsx)": {
        "formats": ["Excel Spreadsheet (.xlsx)"],  # Supported file extensions
        "size_type": "rows",  # Primary measurement unit (rows)
        "size_label": "Number of Rows (1-100,000)",  # UI label for row count
        "size_default": 100,  # Default number of rows
        "size_max": 100000,  # Maximum allowed rows
        "content_type": "columns",  # Secondary measurement unit (columns)
        "content_label": "Number of Columns (1-100)",  # UI label for column count
        "content_default": 10,  # Default number of columns
        "content_max": 100,  # Maximum allowed columns
        "uses_dropdowns": False  # Excel/CSV use text inputs for numeric values
    },
    
    # CSV file configuration
    # Similar to Excel but outputs comma-separated values
    "CSV File (.csv)": {
        "formats": ["CSV File (.csv)"],  # Supported file extensions
        "size_type": "rows",  # Primary measurement unit (rows)
        "size_label": "Number of Rows (1-100,000)",  # UI label for row count
        "size_default": 100,  # Default number of rows
        "size_max": 100000,  # Maximum allowed rows
        "content_type": "columns",  # Secondary measurement unit (columns)
        "content_label": "Number of Columns (1-100)",  # UI label for column count
        "content_default": 10,  # Default number of columns
        "content_max": 100,  # Maximum allowed columns
        "uses_dropdowns": False  # Excel/CSV use text inputs for numeric values
    }
}

# Add PDF option only if ReportLab is available
# PDF generation requires the reportlab library to be installed
if REPORTLAB_AVAILABLE:
    file_format_options["PDF Document (.pdf)"] = {
        "formats": ["PDF Document (.pdf)"],  # Supported file extensions
        "size_type": "pages",  # Measurement unit for document size
        "size_label": "Number of Pages (1-50)",  # UI label for size input
        "size_default": 4,  # Default number of pages
        "size_max": 50,  # Maximum allowed pages
        "content_options": ["whitepaper", "article", "report", "proposal", "design"],  # Available content types
        "content_label": "Document Type",  # UI label for content selection
        "uses_dropdowns": True  # Documents still use dropdowns for content type
    }


def get_file_format_config(format_name: str) -> Optional[FileFormatConfig]:
    """
    Retrieve configuration for a specific file format.
    
    Args:
        format_name (str): The name of the file format to retrieve config for.
                          Must match a key in file_format_options.
    
    Returns:
        Optional[FileFormatConfig]: The configuration dictionary for the format,
                                   or None if the format is not supported.
    
    Example:
        >>> config = get_file_format_config("Excel Spreadsheet (.xlsx)")
        >>> print(config["size_max"])
        100000
    """
    return file_format_options.get(format_name)


def get_supported_formats() -> List[str]:
    """
    Get a list of all supported file formats.
    
    Returns:
        List[str]: A list of supported file format names.
    
    Example:
        >>> formats = get_supported_formats()
        >>> print(formats)
        ['Word Document (.docx)', 'Text File (.txt)', ...]
    """
    return list(file_format_options.keys())


def is_document_format(format_name: str) -> bool:
    """
    Check if a format is a document-based format (uses pages).
    
    Args:
        format_name (str): The name of the file format to check.
    
    Returns:
        bool: True if the format uses pages, False if it uses rows/columns.
    
    Example:
        >>> is_document_format("Word Document (.docx)")
        True
        >>> is_document_format("Excel Spreadsheet (.xlsx)")
        False
    """
    config = get_file_format_config(format_name)
    return config is not None and config.get("size_type") == "pages"


def is_spreadsheet_format(format_name: str) -> bool:
    """
    Check if a format is a spreadsheet-based format (uses rows/columns).
    
    Args:
        format_name (str): The name of the file format to check.
    
    Returns:
        bool: True if the format uses rows/columns, False if it uses pages.
    
    Example:
        >>> is_spreadsheet_format("Excel Spreadsheet (.xlsx)")
        True
        >>> is_spreadsheet_format("Word Document (.docx)")
        False
    """
    config = get_file_format_config(format_name)
    return config is not None and config.get("size_type") == "rows"


def get_max_size(format_name: str) -> Optional[int]:
    """
    Get the maximum size allowed for a specific file format.
    
    Args:
        format_name (str): The name of the file format.
    
    Returns:
        Optional[int]: The maximum size (pages or rows) allowed,
                      or None if format not found.
    
    Example:
        >>> get_max_size("Excel Spreadsheet (.xlsx)")
        100000
        >>> get_max_size("Word Document (.docx)")
        50
    """
    config = get_file_format_config(format_name)
    return config.get("size_max") if config else None


def get_default_size(format_name: str) -> Optional[int]:
    """
    Get the default size for a specific file format.
    
    Args:
        format_name (str): The name of the file format.
    
    Returns:
        Optional[int]: The default size (pages or rows),
                      or None if format not found.
    
    Example:
        >>> get_default_size("Excel Spreadsheet (.xlsx)")
        100
        >>> get_default_size("Word Document (.docx)")
        4
    """
    config = get_file_format_config(format_name)
    return config.get("size_default") if config else None