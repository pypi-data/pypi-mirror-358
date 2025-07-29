"""Python file generator that creates executable Python scripts."""

import sys
from pathlib import Path
from typing import Any, List, Optional, Union

from ...generators import register_generator
from ...utils.file_utils import ensure_directory
from ...validators.base import ValidationResult
from ..base import BaseGenerator


class PythonFileGenerator(BaseGenerator):
    """Generator for Python (.py) script files."""

    @classmethod
    def generate(
        cls,
        content: str,
        output_path: Union[str, Path],
        **kwargs: Any,
    ) -> Path:
        """Generate a Python script file with the given content.

        The generated script will be executable and will print the provided content
        when run. The content will be properly escaped to be valid Python string.

        Args:
            content: The content to include in the script
            output_path: Path where the Python file should be created
            **kwargs: Additional keyword arguments:
                - shebang: Optional shebang line (default: '#!/usr/bin/env python3')
                - docstring: Optional docstring to include at the top of the file
                - imports: Optional list of imports to include
                - main_guard: Whether to wrap the main code in `if __name__ == '__main__'`
                - encoding: File encoding (default: 'utf-8')

        Returns:
            Path to the generated Python file

        Raises:
            OSError: If the file cannot be written
        """
        output_path = Path(output_path)
        ensure_directory(output_path.parent)

        # Get options with defaults
        shebang = kwargs.get("shebang", "#!/usr/bin/env python3")
        docstring = kwargs.get("docstring", "A generated Python script")
        imports = kwargs.get("imports", [])
        main_guard = kwargs.get("main_guard", True)
        encoding = kwargs.get("encoding", "utf-8")

        # Escape the content for Python string
        escaped_content = (
            content.replace("\\", "\\\\")  # Escape backslashes first
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
            .replace("\r", "\\r")
        )

        # Build the script content
        lines = []

        # Add shebang if specified
        if shebang:
            lines.append(f"{shebang}\n")

        # Add file encoding
        lines.append(f"# -*- coding: {encoding} -*-\n")

        # Add docstring
        if docstring:
            lines.append(f'"""{docstring}"""\n')

        # Add imports
        for imp in imports:
            if isinstance(imp, str):
                lines.append(f"import {imp}")
            elif isinstance(imp, (list, tuple)) and len(imp) == 2:
                lines.append(f"from {imp[0]} import {imp[1]}")

        if imports:  # Add a blank line after imports if there are any
            lines.append("")

        # Add main content
        if main_guard:
            lines.append("def main():")
            # Indent the content
            content_lines = [f'    print("{escaped_content}")']
            lines.extend(content_lines)
            lines.append("")
            lines.append("")
            lines.append('if __name__ == "__main__":')
            lines.append("    main()")
        else:
            # Just add the print statement directly
            lines.append(f'print("{escaped_content}")')

        # Ensure there's a trailing newline
        script_content = "\n".join(lines).strip() + "\n"

        # Write the file
        output_path.write_text(script_content, encoding=encoding)

        # Make the file executable (Unix-like systems)
        if shebang and shebang.startswith("#!"):
            try:
                output_path.chmod(0o755)  # rwxr-xr-x
            except (OSError, NotImplementedError):
                # If chmod fails (e.g., on Windows), just continue
                pass

        return output_path

    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> ValidationResult:
        """Validate that the file is a valid Python script.

        This checks both the file extension and attempts to parse the Python code.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid
        """
        from ...validators.text_validator import PythonFileValidator

        return PythonFileValidator.validate(file_path)


# Register the generator for .py extension
@register_generator(["py", "python"])
def generate_py(content: str, output_path: Union[str, Path], **kwargs: Any) -> Path:
    """Generate a Python script file with the given content.

    This is a wrapper around the PythonFileGenerator class to make it work with the
    registration system.
    """
    return PythonFileGenerator.generate(content, output_path, **kwargs)
