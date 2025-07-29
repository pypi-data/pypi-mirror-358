"""Main entry point for the text2file package."""

import sys
from typing import List


def convert_short_syntax(args: List[str]) -> List[str]:
    """Convert short syntax to long syntax.

    Converts: text2file "content" ext1 [ext2...]
    To: text2file generate --content "content" --extension ext1 [ext2...]
    """
    if len(args) >= 2 and not any(
        arg.startswith("--") or arg == "generate" for arg in args
    ):
        # This looks like the short syntax: text2file "content" ext1 [ext2...]
        content = args[0]
        extensions = args[1:]
        return ["generate", "--content", content] + [
            arg for ext in extensions for arg in ("--extension", ext)
        ]
    return args


def main() -> None:
    """Run the text2file CLI application with support for both syntaxes."""
    from .cli import cli

    # Convert short syntax to long syntax if needed
    if (
        len(sys.argv) > 1
        and sys.argv[1] != "--help"
        and not sys.argv[1].startswith("-")
    ):
        sys.argv[1:] = convert_short_syntax(sys.argv[1:])

    cli()


if __name__ == "__main__":
    main()
