"""Markdown file generator that creates well-formatted markdown documents."""

import textwrap
from pathlib import Path
from typing import Any, List, Optional, Union

from ...generators import register_generator
from ...utils.file_utils import ensure_directory
from ...utils.text_utils import wrap_text
from ...validators.base import ValidationResult
from ..base import BaseGenerator


class MarkdownGenerator(BaseGenerator):
    """Generator for Markdown (.md, .markdown) files."""

    @classmethod
    def generate(
        cls,
        content: str,
        output_path: Union[str, Path],
        **kwargs: Any,
    ) -> Path:
        """Generate a markdown file with the given content.

        The generated markdown will include a title, timestamp, and the provided content
        formatted with proper markdown syntax.

        Args:
            content: The main content to include in the markdown
            output_path: Path where the markdown file should be created
            **kwargs: Additional keyword arguments:
                - title: Document title (default: 'Generated Document')
                - author: Optional author name
                - date: Optional date (default: current date)
                - width: Maximum line width (default: 80)
                - add_toc: Whether to add a table of contents (default: False)
                - add_hr: Whether to add a horizontal rule after the header (default: True)
                - encoding: File encoding (default: 'utf-8')

        Returns:
            Path to the generated markdown file

        Raises:
            OSError: If the file cannot be written
        """
        output_path = Path(output_path)
        ensure_directory(output_path.parent)

        # Get options with defaults
        title = kwargs.get("title", "Generated Document")
        author = kwargs.get("author")
        date = kwargs.get("date", None)
        width = int(kwargs.get("width", 80))
        add_toc = bool(kwargs.get("add_toc", False))
        add_hr = bool(kwargs.get("add_hr", True))
        encoding = kwargs.get("encoding", "utf-8")

        # Import datetime here to avoid loading it when not needed
        from datetime import datetime

        # Format date if not provided
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build the markdown content
        lines = []

        # Add title
        lines.append(f"# {title}\n")

        # Add metadata
        if author or date:
            meta = []
            if author:
                meta.append(f"**Author:** {author}")
            if date:
                meta.append(f"**Date:** {date}")
            lines.append(" | ".join(meta) + "\n")

        # Add horizontal rule if requested
        if add_hr:
            lines.append("---\n")

        # Add table of contents if requested
        if add_toc:
            lines.append("## Table of Contents\n")
            # Add placeholder for TOC - in a real implementation, you'd parse the content
            lines.append("* [Introduction](#introduction)\n")
            lines.append("* [Usage](#usage)\n")
            lines.append("* [Examples](#examples)\n\n")

        # Add the main content with proper wrapping
        wrapped_content = wrap_text(content, width=width)
        lines.append(wrapped_content)

        # Ensure there's a trailing newline
        markdown_content = "\n".join(lines).strip() + "\n"

        # Write the file
        output_path.write_text(markdown_content, encoding=encoding)

        return output_path

    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> ValidationResult:
        """Validate that the file is a valid markdown file.

        This checks:
        1. File exists and is readable
        2. File has a valid markdown extension
        3. File contains valid markdown syntax (basic checks)

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid markdown
        """
        from ...validators.text_validator import MarkdownValidator

        return MarkdownValidator.validate(file_path)


# Register the generator for .md and .markdown extensions
@register_generator(["md", "markdown"])
def generate_md(content: str, output_path: Union[str, Path], **kwargs: Any) -> Path:
    """Generate a markdown file with the given content.

    This is a wrapper around the MarkdownGenerator class to make it work with the
    registration system.
    """
    return MarkdownGenerator.generate(content, output_path, **kwargs)
