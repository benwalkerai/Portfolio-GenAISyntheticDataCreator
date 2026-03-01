#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
from datetime import datetime

from config.logging_config import setup_logging
from generators.data_generator import SyntheticDataGenerator


def parse_args():
    p = argparse.ArgumentParser(description="Generate synthetic data (CSV/XLSX) via CLI")
    fmt = p.add_mutually_exclusive_group(required=True)
    
    fmt.add_argument("--csv", action="store_true", help="Generate CSV output")
    fmt.add_argument("--xlsx", action="store_true", help="Generate Excel (.xlsx) output")
    
    fmt.add_argument("--md", action="store_true", help="Generate Markdown (.md) document output")
    fmt.add_argument("--docx", action="store_true", help="Generate Word (.docx) document output")
    fmt.add_argument("--pdf", action="store_true", help="Generate PDF (.pdf) document output")
    fmt.add_argument("--txt", action="store_true", help="Generate Text (.txt) document output")

    p.add_argument("--subject", required=True, help="Subject/topic to guide LLM generation")

    p.add_argument("--rows", type=int, default=100, help="Number of rows (1-100000)")
    p.add_argument("--columns", "--col", dest="columns", type=int, default=10, help="Number of columns (1-100)")

    p.add_argument("--pages", type=int, default=3, help="Number of pages for documents")
    p.add_argument(
        "--doc-type",
        choices=["whitepaper", "article", "report", "proposal", "design"],
        default="article",
        help="Document content type"
    )

    p.add_argument("-d", "--dest", default=".", help="Destination directory to write the generated file")
    
    p.add_argument("--no-correlations", action="store_true", help="Disable correlation enforcement (totals, ages, dates)")
    p.add_argument("--allow-future", action="store_true", help="Allow future dates")
    p.add_argument("--no-distributions", action="store_true", help="Disable realistic distributions")
    p.add_argument("--missingness", type=float, default=0.0, help="Missingness rate (0.0-0.3)")
    p.add_argument("--noise", type=float, default=0.0, help="Noise level for text (0.0-0.2)")
    
    return p.parse_args()


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def sanitize_filename(s):
    keep = [c if c.isalnum() or c in ("-", "_") else "-" for c in s.strip()]
    out = "".join(keep).strip("-")
    return out or "dataset"


def main():
    setup_logging()
    
    args = parse_args()

    file_format = "CSV File (.csv)" if args.csv else "Excel Spreadsheet (.xlsx)"

    options = {
        "enforce_correlations": not args.no_correlations,
        "prevent_future": not args.allow_future,
        "apply_distributions": not args.no_distributions,
        "add_missingness": args.missingness > 0.0,
        "missingness_rate": max(0.0, min(0.3, float(args.missingness))),
        "add_noise": args.noise > 0.0,
        "noise_level": max(0.0, min(0.2, float(args.noise))),
    }

    gen = SyntheticDataGenerator()

    if args.csv or args.xlsx:
        temp_path, status_msg, _preview_df = gen.generate_data_file(
            rows=args.rows,
            columns=args.columns,
            subject=args.subject,
            file_format=file_format,
            options=options,
        )

        if not temp_path:
            print(status_msg or "Error: generation failed", file=sys.stderr)
            return 1

        ensure_dir(args.dest)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = sanitize_filename(args.subject)
        ext = ".csv" if args.csv else ".xlsx"
        out_name = f"{base_name}_{args.rows}x{args.columns}_{timestamp}{ext}"
        dest_path = os.path.join(args.dest, out_name)

        try:
            shutil.copyfile(temp_path, dest_path)
        except Exception:
            shutil.move(temp_path, dest_path)

        print(status_msg)
        print(f"Output: {dest_path}")
        return 0

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
        doc_format = None
        ext = ".md"

    ensure_dir(args.dest)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = sanitize_filename(args.subject)

    if args.md:
        doc_gen = gen.document_generator
        if int(args.pages) >= 3:
            content = doc_gen.generate_document_content_iterative(args.doc_type, int(args.pages), args.subject)
        else:
            content = doc_gen.generate_document_content(args.doc_type, int(args.pages), args.subject)
        
        dest_path = os.path.join(args.dest, f"{base_name}_{args.doc_type}_{args.pages}p_{timestamp}.md")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {args.pages}-page {args.doc_type} about '{args.subject}' (Markdown)")
        print(f"Output: {dest_path}")
        return 0
    else:
        temp_path, status_msg = gen.document_generator.generate_document(
            content_type=args.doc_type,
            pages=int(args.pages),
            subject=args.subject,
            file_format=doc_format,
        )
        
        if not temp_path:
            print(status_msg or "Error: generation failed", file=sys.stderr)
            return 1
        
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
