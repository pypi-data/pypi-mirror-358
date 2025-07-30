"""Command line interface for proj2pdf."""

import os
import glob
import tempfile
from PyPDF2 import PdfMerger
import argparse
from .converters import (convert_code_to_html, convert_md_to_html,
                         convert_ipynb_to_html, html_to_pdf)


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    process_files(args.directory, args.output, args.file_types, args.exclude)


def process_files(root_dir='.',
                  output_pdf='combined_output.pdf',
                  file_types=None,
                  exclude_patterns=None):
    """Process and combine files into a single PDF."""
    # Default file types if none specified
    if file_types is None:
        file_types = [
            'md', 'ipynb', 'py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs',
            'rb', 'php', 'cs', 'scala', 'kt', 'swift', 'r', 'sql', 'sh', 'pdf'
        ]

    # Create a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_files = []

        # First, collect all files and sort them
        all_files = []
        # Add files based on specified types
        for ext in file_types:
            pattern = f'**/*.{ext}'
            all_files.extend(
                glob.glob(os.path.join(root_dir, pattern), recursive=True))

        # Filter out excluded patterns
        if exclude_patterns:
            for pattern in exclude_patterns:
                all_files = [
                    f for f in all_files
                    if not glob.fnmatch.fnmatch(f, pattern)
                ]

        # Sort files by path
        all_files.sort()

        # Process each file
        for i, filepath in enumerate(all_files):
            print(f"Processing {filepath}...")

            try:
                if filepath.endswith('.pdf'):
                    # For PDF files, just add them to the list
                    pdf_files.append(filepath)
                else:
                    # For non-PDF files, convert them
                    html_path = os.path.join(temp_dir, f'doc_{i}.html')
                    pdf_path = os.path.join(temp_dir, f'doc_{i}.pdf')

                    if filepath.endswith('.md'):
                        convert_md_to_html(filepath, html_path)
                    elif filepath.endswith('.ipynb'):
                        convert_ipynb_to_html(filepath, html_path)
                    else:
                        # All other files are treated as code files
                        convert_code_to_html(filepath, html_path)

                    # Convert HTML to PDF
                    html_to_pdf(html_path, pdf_path)
                    pdf_files.append(pdf_path)
            except Exception as e:
                print(f"⚠️ Failed to process {filepath}: {str(e)}")
                continue

        if pdf_files:
            # Merge all PDFs
            merger = PdfMerger()
            for pdf_file in pdf_files:
                try:
                    merger.append(pdf_file)
                except Exception as e:
                    print(f"⚠️ Failed to merge {pdf_file}: {str(e)}")
                    continue

            merger.write(output_pdf)
            merger.close()
            print(f"\n✅ All files merged into: {output_pdf}")
        else:
            print("\n⚠️ No files were processed successfully.")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=
        'Convert and merge various file types (code, markdown, notebooks, PDFs) into a single PDF.',
        epilog=
        'Supported code file types: .py, .js, .ts, .java, .cpp, .c, .go, .rs, .rb, .php, .cs, .scala, .kt, .swift, .r, .sql, .sh (and more)'
    )
    parser.add_argument(
        '-d',
        '--directory',
        default='.',
        help='Root directory to search for files (default: current directory)')
    parser.add_argument(
        '-o',
        '--output',
        default='combined_output.pdf',
        help='Output PDF file name (default: combined_output.pdf)')
    parser.add_argument(
        '-t',
        '--file-types',
        nargs='+',
        help='File types to include (default: all supported types)')
    parser.add_argument('-e',
                        '--exclude',
                        nargs='+',
                        help='Glob patterns for files to exclude')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
