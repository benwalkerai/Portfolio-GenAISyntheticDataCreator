#!/usr/bin/env python3
"""
Command-line entrypoint for Synthetic Data Generator

This module provides a comprehensive command-line interface for generating synthetic
data files and documents without using the web UI. It offers the same generation
capabilities as the Gradio interface but through a terminal-based workflow.

Key Features:
- Generate CSV and Excel data files with realistic data
- Create professional documents in multiple formats
- Advanced data realism options via command-line flags
- Batch processing capabilities
- Flexible output directory configuration
- Integration with the same generation pipeline as the web UI

Supported Output Formats:
- Data Files: CSV (.csv), Excel (.xlsx)
- Documents: Word (.docx), PDF (.pdf), Text (.txt), Markdown (.md)

Usage Examples:
    # Data files
    python create_data.py --csv --subject "Financial records" --rows 1000 --columns 25 -d C:\\Temp\\synth-data
    python create_data.py --xlsx --subject "Product catalog" --rows 500 --columns 12 -d C:\\Temp\\synth-data

    # Documents
    python create_data.py --md --subject "AI Governance" --pages 4 --doc-type report -d C:\\Temp\\synth-docs
    python create_data.py --docx --subject "Zero Trust Security" --pages 5 --doc-type whitepaper -d C:\\Temp\\synth-docs
    python create_data.py --pdf --subject "Cloud Cost Optimization" --pages 3 --doc-type article -d C:\\Temp\\synth-docs
    python create_data.py --txt --subject "SRE Playbook" --pages 2 --doc-type design -d C:\\Temp\\synth-docs

This CLI calls the same generators used by the Gradio UI, ensuring consistency
between web and command-line interfaces.

Author: Ben Walker (https://github.com/benwalkerai)
Version: 1.0.0
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from config.logging_config import setup_logging
from generators.data_generator import SyntheticDataGenerator


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the synthetic data generator.
    
    This function defines and parses all command-line arguments for both data
    file generation and document creation. It provides comprehensive options
    for controlling data realism, output format, and generation parameters.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
        
    Raises:
        SystemExit: If argument parsing fails or invalid arguments provided
    """
    p = argparse.ArgumentParser(description="Generate synthetic data (CSV/XLSX) via CLI")
    fmt = p.add_mutually_exclusive_group(required=True)
    
    # Data file output formats
    fmt.add_argument("--csv", action="store_true", help="Generate CSV output")
    fmt.add_argument("--xlsx", action="store_true", help="Generate Excel (.xlsx) output")
    
    # Document output formats
    fmt.add_argument("--md", action="store_true", help="Generate Markdown (.md) document output")
    fmt.add_argument("--docx", action="store_true", help="Generate Word (.docx) document output")
    fmt.add_argument("--pdf", action="store_true", help="Generate PDF (.pdf) document output")
    fmt.add_argument("--txt", action="store_true", help="Generate Text (.txt) document output")

    # Required subject/topic for generation
    p.add_argument("--subject", required=True, help="Subject/topic to guide LLM generation")

    # Data generation options
    p.add_argument("--rows", type=int, default=100, help="Number of rows (1-100000)")
    p.add_argument("--columns", "--col", dest="columns", type=int, default=10, help="Number of columns (1-100)")

    # Document generation options
    p.add_argument("--pages", type=int, default=3, help="Number of pages for documents")
    p.add_argument(
        "--doc-type",
        choices=["whitepaper", "article", "report", "proposal", "design"],
        default="article",
        help="Document content type"
    )

    # Output configuration
    p.add_argument("-d", "--dest", default=".", help="Destination directory to write the generated file")
    
    # Data realism options (mirroring UI advanced options)
    p.add_argument("--no-correlations", action="store_true", help="Disable correlation enforcement (totals, ages, dates)")
    p.add_argument("--allow-future", action="store_true", help="Allow future dates")
    p.add_argument("--no-distributions", action="store_true", help="Disable realistic distributions")
    p.add_argument("--missingness", type=float, default=0.0, help="Missingness rate (0.0-0.3)")
    p.add_argument("--noise", type=float, default=0.0, help="Noise level for text (0.0-0.2)")
    
    return p.parse_args()


def ensure_dir(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    This utility function creates directories recursively if they don't exist,
    similar to `mkdir -p` in Unix systems. It's safe to call multiple times
    as it won't raise an error if the directory already exists.
    
    Args:
        path (str): Directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)


def sanitize_filename(s: str) -> str:
    """
    Sanitize a string to create a valid filename.
    
    This function converts a string into a safe filename by:
    - Removing or replacing invalid characters with hyphens
    - Keeping only alphanumeric characters, hyphens, and underscores
    - Stripping leading/trailing hyphens
    - Providing a fallback name if the result is empty
    
    Args:
        s (str): Input string to sanitize
        
    Returns:
        str: Sanitized filename safe for use in file systems
        
    Example:
        >>> sanitize_filename("My Data Set!")
        "My-Data-Set"
        >>> sanitize_filename("!!!")
        "dataset"
    """
    keep = [c if c.isalnum() or c in ("-", "_") else "-" for c in s.strip()]
    out = "".join(keep).strip("-")
    return out or "dataset"


def main() -> int:
    """
    Main entry point for the command-line synthetic data generator.
    
    This function orchestrates the entire data generation process, handling both
    data files (CSV/Excel) and documents (Word/PDF/Text/Markdown). It processes
    command-line arguments, configures generation options, and manages file output.
    
    The function branches into two main paths:
    1. Data file generation (CSV/Excel) using the data generator
    2. Document generation (Word/PDF/Text/Markdown) using the document generator
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
        
    Raises:
        SystemExit: If critical errors occur during generation
    """
    # Initialize logging
    setup_logging()
    
    args = parse_args()

    # Determine file format for data generation
    file_format = "CSV File (.csv)" if args.csv else "Excel Spreadsheet (.xlsx)"

    # Build options aligned with utils.helpers.generate_synthetic_data
    # These options control data realism and quality
    options: Dict[str, Any] = {
        "enforce_correlations": not args.no_correlations,
        "prevent_future": not args.allow_future,
        "apply_distributions": not args.no_distributions,
        "add_missingness": args.missingness > 0.0,
        "missingness_rate": max(0.0, min(0.3, float(args.missingness))),
        "add_noise": args.noise > 0.0,
        "noise_level": max(0.0, min(0.2, float(args.noise))),
    }

    # Initialize the synthetic data generator
    gen = SyntheticDataGenerator()

    # Branch: Data file generation vs Document generation
    if args.csv or args.xlsx:
        # ===== DATA FILE GENERATION =====
        # Generate using the same path as the UI pipeline (returns temp file)
        temp_path, status_msg, _preview_df = gen.generate_data_file(
            rows=args.rows,
            columns=args.columns,
            subject=args.subject,
            file_format=file_format,
            options=options,
        )

        # Check if generation was successful
        if not temp_path:
            print(status_msg or "Error: generation failed", file=sys.stderr)
            return 1

        # Prepare destination path and move/copy the file
        ensure_dir(args.dest)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = sanitize_filename(args.subject)
        ext = ".csv" if args.csv else ".xlsx"
        out_name = f"{base_name}_{args.rows}x{args.columns}_{timestamp}{ext}"
        dest_path = os.path.join(args.dest, out_name)

        # Copy file to destination (fallback to move if copy fails)
        try:
            shutil.copyfile(temp_path, dest_path)
        except Exception:
            # Fallback to move if copy fails
            shutil.move(temp_path, dest_path)

        print(status_msg)
        print(f"Output: {dest_path}")
        return 0

    # ===== DOCUMENT GENERATION =====
    # Map command-line flags to file_format strings expected by DocumentGenerator
    if args.docx:
        doc_format = "Word Document (.docx)"
        ext = ".docx"
    elif args.pdf:
        doc_format = "PDF Document (.pdf)"
        ext = ".pdf"
    elif args.txt:
        doc_format = "Text File (.txt)"
        ext = ".txt"
    else:
        doc_format = None  # Markdown handled separately
        ext = ".md"

    # Prepare output directory and filename components
    ensure_dir(args.dest)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = sanitize_filename(args.subject)

    if args.md:
        # ===== MARKDOWN GENERATION =====
        # Produce Markdown content using the same content routines as DocumentGenerator
        # Use iterative for >=3 pages to keep parity with document generation
        doc_gen = gen.document_generator
        if int(args.pages) >= 3:
            content = doc_gen.generate_document_content_iterative(args.doc_type, int(args.pages), args.subject)
        else:
            content = doc_gen.generate_document_content(args.doc_type, int(args.pages), args.subject)
        
        # Write markdown content directly to file
        dest_path = os.path.join(args.dest, f"{base_name}_{args.doc_type}_{args.pages}p_{timestamp}.md")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {args.pages}-page {args.doc_type} about '{args.subject}' (Markdown)")
        print(f"Output: {dest_path}")
        return 0
    else:
        # ===== BINARY DOCUMENT GENERATION =====
        # Generate binary documents (Word/PDF/Text) using DocumentGenerator
        temp_path, status_msg = gen.document_generator.generate_document(
            content_type=args.doc_type,
            pages=int(args.pages),
            subject=args.subject,
            file_format=doc_format,
        )
        
        # Check if generation was successful
        if not temp_path:
            print(status_msg or "Error: generation failed", file=sys.stderr)
            return 1
        
        # Copy generated document to destination
        dest_path = os.path.join(args.dest, f"{base_name}_{args.doc_type}_{args.pages}p_{timestamp}{ext}")
        try:
            shutil.copyfile(temp_path, dest_path)
        except Exception:
            shutil.move(temp_path, dest_path)
        print(status_msg)
        print(f"Output: {dest_path}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
