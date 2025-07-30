"""File conversion utilities for proj2pdf."""

import os
import nbformat
from nbconvert import HTMLExporter
from markdownify import markdownify as md2html
from playwright.sync_api import sync_playwright
import pygments
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.util import ClassNotFound


def convert_code_to_html(code_path, output_path):
    """Convert any code file to HTML with syntax highlighting"""
    with open(code_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Try to get a lexer based on the filename
    try:
        lexer = get_lexer_for_filename(code_path)
    except ClassNotFound:
        # If no lexer is found, use plain text
        lexer = TextLexer()

    # Generate CSS for syntax highlighting
    formatter = HtmlFormatter(style='monokai', full=True)
    css = formatter.get_style_defs()

    # Highlight the code
    highlighted_code = highlight(code, lexer, formatter)

    # Add custom CSS for better presentation
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            {css}
            body {{ 
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                background: white;
            }}
            .filename {{
                font-family: 'Courier New', monospace;
                font-size: 1.2em;
                color: #333;
                margin-bottom: 20px;
                padding: 10px;
                background: #f5f5f5;
                border-radius: 5px;
            }}
            .highlight {{
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .language-info {{
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                color: #666;
                margin-top: -15px;
                margin-bottom: 15px;
                padding-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="filename">{os.path.basename(code_path)}</div>
        <div class="language-info">Language: {lexer.name}</div>
        {highlighted_code}
    </body>
    </html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def convert_md_to_html(md_path, output_path):
    """Convert markdown to HTML"""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = md2html(md_content, heading_style="ATX")

    # Wrap in basic HTML structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
            code {{ font-family: 'Courier New', monospace; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <div class="filename">{os.path.basename(md_path)}</div>
        {html_content}
    </body>
    </html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)


def convert_ipynb_to_html(ipynb_path, output_path):
    """Convert Jupyter notebook to HTML"""
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Configure and create the HTML exporter
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'

    # Convert notebook to HTML
    html_content, _ = html_exporter.from_notebook_node(nb)

    # Add filename at the top
    html_content = f"""
    <div style="font-family: 'Courier New', monospace; font-size: 1.2em; color: #333; margin-bottom: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px;">
        {os.path.basename(ipynb_path)}
    </div>
    {html_content}
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF using Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f'file://{os.path.abspath(html_path)}')
        # Add a small delay to ensure all styles are loaded
        page.wait_for_timeout(1000)
        page.pdf(path=pdf_path, format='A4')
        browser.close()
