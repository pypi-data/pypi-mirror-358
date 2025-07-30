"""
markdown-html-pdf: A powerful Python package to convert Markdown files to PDF.

This package provides functionality to convert Markdown documents to PDF files
with syntax highlighting, emoji support, and professional formatting.
"""

from .html_to_pdf import html_to_pdf
from .markdown_html_pdf import markdown_html_pdf
from .markdown_to_html import markdown_to_html

__version__ = "0.1.0"
__author__ = "Gustavo Casadei Bellanda"
__email__ = "bellanda.dev@outlook.com"

__all__ = [
    "markdown_html_pdf",
    "markdown_to_html",
    "html_to_pdf",
]
