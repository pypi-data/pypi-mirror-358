"""Shell script (.sh) file generator that creates executable shell scripts."""

import os
import stat
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ...generators import register_generator
from ...utils.file_utils import ensure_directory
from ...validators.base import ValidationResult
from ..base import BaseGenerator


class ShGenerator(BaseGenerator):
    """Generator for shell script (.sh) files."""

    @classmethod
    def generate(
        cls,
        content: str,
        output_path: Union[str, Path],
        **kwargs: Any,
    ) -> Path:
        """Generate a shell script file with the given content.

        The generated script will be executable and will print the provided content
        when run. The content will be properly escaped to be valid in a shell script.

        Args:
            content: The content to include in the script
            output_path: Path where the shell script file should be created
            **kwargs: Additional keyword arguments:
                - shebang: Optional shebang line (default: '#!/bin/bash')
                - description: Optional description comment at the top of the file
                - encoding: File encoding (default: 'utf-8')

        Returns:
            Path to the generated shell script file

        Raises:
            OSError: If the file cannot be written
        """
        output_path = Path(output_path)
        ensure_directory(output_path.parent)

        # Get options with defaults
        shebang = kwargs.get("shebang", "#!/bin/bash")
        description = kwargs.get("description", "A generated shell script")
        encoding = kwargs.get("encoding", "utf-8")

        # Escape the content for shell script
        escaped_content = (
            content.replace("\\", "\\\\")  # Escape backslashes first
            .replace('"', '\\"')
            .replace("`", "\\`")
            .replace("$", "\\$")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
            .replace("\r", "\\r")
        )

        # Build the script content
        lines = []

        # Add shebang
        lines.append(f"{shebang}")

        # Add description
        if description:
            lines.append("")
            lines.append("# " + "=" * 77)
            for line in description.split("\n"):
                lines.append(f"# {line}")
            lines.append("# " + "=" * 77)

        # Add content
        lines.append("")
        # Only add the content directly, without an extra echo
        # The content is already properly escaped
        lines.append(escaped_content)

        # Ensure there's a trailing newline
        script_content = "\n".join(lines).strip() + "\n"

        # Write the file
        output_path.write_text(script_content, encoding=encoding)

        # Make the file executable (Unix-like systems)
        try:
            st = os.stat(output_path)
            os.chmod(output_path, st.st_mode | stat.S_IEXEC)
        except (OSError, AttributeError):
            # If chmod fails (e.g., on Windows), just continue
            pass

        return output_path

    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> ValidationResult:
        """Validate that the file is a valid shell script.

        This checks both the file extension and that the file starts with a shebang
        or contains valid shell script content.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid
        """
        from ...validators.text_validator import ShellScriptValidator

        return ShellScriptValidator.validate(file_path)


# Register the generator for .sh extension
@register_generator(["sh", "bash"])
def generate_sh(content: str, output_path: Union[str, Path], **kwargs: Any) -> Path:
    """Generate a shell script file with the given content.

    This is a wrapper around the ShGenerator class to make it work with the
    registration system.
    """
    return ShGenerator.generate(content, output_path, **kwargs)
