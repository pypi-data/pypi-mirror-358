"""Command-line interface for markdown-html-pdf."""

import asyncio
import pathlib
import sys
from typing import Optional

import click
from playwright.async_api import async_playwright

try:
    from .markdown_html_pdf import markdown_html_pdf
except ImportError:
    from markdown_html_pdf import markdown_html_pdf


async def install_browsers():
    """Install Playwright browsers."""
    async with async_playwright() as p:
        await p.chromium.launch()


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument("output_file", type=click.Path(path_type=pathlib.Path))
@click.option("--title", "-t", default=None, help="Title for the PDF document")
@click.option("--install-browsers", is_flag=True, help="Install Playwright browsers before conversion")
def main(
    input_file: pathlib.Path,
    output_file: pathlib.Path,
    title: Optional[str],
    install_browsers: bool,
) -> None:
    """Convert Markdown files to PDF with syntax highlighting and emoji support.

    INPUT_FILE: Path to the input Markdown file
    OUTPUT_FILE: Path where the PDF file will be saved
    """
    # Use filename as title if not provided
    if title is None:
        title = input_file.stem

    async def run_conversion():
        try:
            if install_browsers:
                click.echo("Installing Playwright browsers...")
                try:
                    await install_browsers()
                    click.echo("✓ Browsers installed successfully")
                except Exception as e:
                    click.echo(f"⚠ Browser installation failed: {e}")
                    click.echo("Continuing with conversion...")

            click.echo(f"Converting {input_file} to {output_file}...")
            await markdown_html_pdf(
                markdown_file_path=input_file,
                pdf_output_file_path=output_file,
                html_output_title=title,
            )
            click.echo(f"✓ Successfully converted to {output_file}")

        except Exception as e:
            click.echo(f"✗ Conversion failed: {e}", err=True)
            sys.exit(1)

    # Run the async function
    asyncio.run(run_conversion())


if __name__ == "__main__":
    main()
