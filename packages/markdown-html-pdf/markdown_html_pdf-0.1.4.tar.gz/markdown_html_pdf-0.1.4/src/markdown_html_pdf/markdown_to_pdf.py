"""Main module for converting Markdown to PDF."""

import asyncio
import pathlib
import tempfile
from typing import Union

from markdown_html_pdf.constants import paths
from markdown_html_pdf.html_to_pdf import html_to_pdf
from markdown_html_pdf.markdown_to_html import markdown_to_html


async def markdown_to_pdf(
    markdown_file_path: Union[str, pathlib.Path], pdf_output_file_path: Union[str, pathlib.Path], html_output_title: str
) -> None:
    """Convert Markdown file to PDF with syntax highlighting and emoji support.

    Args:
        markdown_file_path: Path to the input Markdown file
        pdf_output_file_path: Path where the PDF file will be saved
        html_output_title: Title for the HTML document and PDF
    """
    # Create a temporary directory for HTML files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_html_file_path = pathlib.Path(temp_dir) / f"{html_output_title}.html"

        # Convert markdown to html
        markdown_to_html(
            markdown_file_path,
            temp_html_file_path,
            html_output_title,
        )

        # Convert html to pdf
        await html_to_pdf(temp_html_file_path, pdf_output_file_path)

        # Temporary file is automatically cleaned up when exiting the context


if __name__ == "__main__":
    asyncio.run(
        markdown_to_pdf(
            markdown_file_path=paths.MARKDOWN_DIR / "example.md",
            pdf_output_file_path=paths.PDF_DIR / "example.pdf",
            html_output_title="Example",
        )
    )
