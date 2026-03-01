try:
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

_doc_fmt = {"size_type": "pages", "size_label": "Number of Pages (1-50)", "size_default": 4, "size_max": 50, "content_options": ["whitepaper", "article", "report", "proposal", "design"], "content_label": "Document Type", "uses_dropdowns": True}
_sheet_fmt = {"size_type": "rows", "size_label": "Number of Rows (1-100,000)", "size_default": 100, "size_max": 100000, "content_type": "columns", "content_label": "Number of Columns (1-100)", "content_default": 10, "content_max": 100, "uses_dropdowns": False}

file_format_options = {
    "Word Document (.docx)": {**_doc_fmt, "formats": ["Word Document (.docx)"]},
    "Text File (.txt)": {**_doc_fmt, "formats": ["Text File (.txt)"]},
    "Excel Spreadsheet (.xlsx)": {**_sheet_fmt, "formats": ["Excel Spreadsheet (.xlsx)"]},
    "CSV File (.csv)": {**_sheet_fmt, "formats": ["CSV File (.csv)"]}
}

if REPORTLAB_AVAILABLE:
    file_format_options["PDF Document (.pdf)"] = {**_doc_fmt, "formats": ["PDF Document (.pdf)"]}


def get_file_format_config(format_name):
    return file_format_options.get(format_name)


def get_supported_formats():
    return list(file_format_options.keys())


def is_document_format(format_name):
    config = get_file_format_config(format_name)
    return config is not None and config.get("size_type") == "pages"


def is_spreadsheet_format(format_name):
    config = get_file_format_config(format_name)
    return config is not None and config.get("size_type") == "rows"


def get_max_size(format_name):
    config = get_file_format_config(format_name)
    return config.get("size_max") if config else None


def get_default_size(format_name):
    config = get_file_format_config(format_name)
    return config.get("size_default") if config else None