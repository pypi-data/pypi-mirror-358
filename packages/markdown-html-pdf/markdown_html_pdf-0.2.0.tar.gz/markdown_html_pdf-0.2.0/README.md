# markdown-html-pdf

A powerful Python package to convert Markdown files to PDF with syntax highlighting and emoji support.

## Features

- ✨ Convert Markdown to PDF with beautiful formatting
- 🎨 Syntax highlighting for code blocks
- 😀 Full emoji support
- 🔧 GitHub-flavored Markdown support
- 📱 Responsive design optimized for print
- 🚀 Fast conversion using Playwright
- 💻 Command-line interface
- 🐍 Python API

## Installation

```bash
uv add markdown-html-pdf
```

After installation, you need to install Playwright browsers:

```bash
uv run playwright install
```

Or use the built-in auto-installer on first run.

## Usage

### Command Line

```bash
# Basic conversion
uv run markdown-html-pdf input.md output.pdf

# With custom title
uv run markdown-html-pdf input.md output.pdf --title "My Document"

# Install browsers first (useful for first run)
uv run markdown-html-pdf input.md output.pdf --install-browsers
```

You can also use the shorter alias:

```bash
md2pdf input.md output.pdf
```

### Python API

```python
import asyncio
from markdown_html_pdf import markdown_html_pdf

async def convert():
    await markdown_html_pdf(
        markdown_file_path="input.md",
        pdf_output_file_path="output.pdf",
        html_output_title="My Document"
    )

asyncio.run(convert())
```

## Requirements

- Python 3.12+
- Playwright (automatically installed)

## How it works

1. **Markdown to HTML**: Converts Markdown to HTML using `markdown-it-py` with GitHub-flavored Markdown support
2. **Syntax Highlighting**: Applies syntax highlighting to code blocks using Pygments
3. **HTML to PDF**: Uses Playwright to render HTML to PDF with optimized settings for text fidelity

## Supported Markdown Features

- Headers (H1-H6)
- **Bold** and _italic_ text
- `Inline code` and code blocks with syntax highlighting
- Links and images
- Tables
- Lists (ordered and unordered)
- Blockquotes
- Horizontal rules
- Emojis 😎

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
