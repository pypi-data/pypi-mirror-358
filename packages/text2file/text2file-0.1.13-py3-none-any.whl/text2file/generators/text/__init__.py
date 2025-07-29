"""Text file generators."""

import csv
import json
import sys
from pathlib import Path

from ...generators import register_generator
from .markdown_generator import MarkdownGenerator
from .python_generator import PythonFileGenerator
from .sh_generator import ShGenerator

print(f"Loading text generator from {__file__}", file=sys.stderr)


@register_generator(["txt", "md", "html", "css", "js", "py", "json", "csv"])
def generate_text_file(content: str, output_path: Path, **kwargs) -> Path:
    """Generate a text file with the given content.

    Args:
        content: Text content to write to the file
        output_path: Path where the file should be created
        **kwargs: Additional keyword arguments

    Returns:
        Path to the created file
    """
    print(f"Generating text file: {output_path}", file=sys.stderr)
    # If it's a markdown file, don't modify the content
    if output_path.suffix.lower() in [".md", ".markdown"]:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ext = output_path.suffix.lower()[1:]  # Remove the dot

    if ext == "json":
        # Try to parse as JSON, fall back to raw content if invalid
        try:
            json_data = json.loads(content)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
            return output_path
        except json.JSONDecodeError:
            # If content is not valid JSON, save as plain text
            pass
    elif ext == "csv":
        # Try to parse as CSV, fall back to raw content if invalid
        try:
            # Split content into lines and then into cells
            rows = [line.split(",") for line in content.split("\n") if line.strip()]
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            return output_path
        except Exception:
            # If CSV parsing fails, save as plain text
            pass
    elif ext == "py":
        # For Python files, create a proper script with the content in a print
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# -*- coding: utf-8 -*-\n\n")
            f.write("def main():\n")
            # Escape triple quotes and handle multi-line content
            escaped_content = content.replace('"""', '\\"\\"\\"')
            f.write(f'    print("""{escaped_content}""")\n\n')
            f.write('if __name__ == "__main__":\n')
            f.write("    main()\n")
        # Make the file executable
        output_path.chmod(0o755)
        return output_path

    # For all other text formats, write the content as is
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


__all__ = [
    "PythonFileGenerator",
    "MarkdownGenerator",
    "ShGenerator",
    "generate_text_file",
]
