#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cli.py - CLI interface for flat-ray
"""

import argparse
import os
import sys
import time
from flat_ray.analyzer import analyze_directory


def validate_directory(path: str) -> str:
    """
    Ensure the given path is a valid directory.

    Args:
        path (str): Path to validate.

    Returns:
        str: The same path if valid.

    Raises:
        argparse.ArgumentTypeError: If the path is not a directory.
    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Invalid directory: {path}")
    return path


def validate_output_path(path: str) -> str:
    """
    Ensure the output file's directory exists.

    Args:
        path (str): Output file path to validate.

    Returns:
        str: The same path if the directory exists.

    Raises:
        argparse.ArgumentTypeError: If the directory does not exist.
    """
    out_dir = os.path.dirname(os.path.abspath(path))
    if out_dir and not os.path.exists(out_dir):
        raise argparse.ArgumentTypeError(f"Output directory does not exist: {out_dir}")
    return path


def main() -> None:
    """
    Main CLI entry point for flat-ray XML/HTML analyzer.
    Parses arguments and launches the analysis process.
    """
    parser = argparse.ArgumentParser(
        description="flat-ray: A tolerant XML/HTML CLI analyzer for structure inspection"
    )

    parser.add_argument("directory", type=validate_directory,
                        help="Directory containing XML/HTML files to analyze")
    parser.add_argument("-o", "--output", type=validate_output_path, default="report.json",
                        help="Path to output JSON report (default: report.json)")
    parser.add_argument("--max-values", type=int, default=-1,
                        help="Maximum values to keep per attribute or element text (default: 1000)")
    parser.add_argument("--ext", nargs="+", default=[".xml", ".html", ".txt"],
                        help="File extensions to analyze (default: .xml .html .txt)")
    parser.add_argument("--display-format", choices=["tree", "list", "flat", "tree-flat"],
                        default="tree-flat", help="Output display format in terminal (default: tree-flat)")
    parser.add_argument("--text-output", default="output.txt",
                        help="Optional text file to save the terminal summary")
    parser.add_argument("--sample-csv", default="samples.csv",
                        help="CSV output for sampled attribute values and element contents")
    parser.add_argument("--n-jobs", type=int, default=-1,
                        help="Number of parallel workers (default: -1 = all cores)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Display analysis summary in the terminal")

    args = parser.parse_args()

    try:
        start_time = time.time()
        analyze_directory(
            input_dir=args.directory,
            output_path=args.output,
            max_values=args.max_values,
            extensions=tuple(args.ext),
            verbose=args.verbose,
            display_format=args.display_format,
            text_output=args.text_output,
            sample_csv=args.sample_csv,
            n_jobs=args.n_jobs
        )
        elapsed_time = time.time() - start_time
        print(f"[TERMINATED IN {elapsed_time:.2f} secs]")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
