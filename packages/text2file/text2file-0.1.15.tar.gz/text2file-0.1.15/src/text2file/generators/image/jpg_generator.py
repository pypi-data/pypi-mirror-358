"""JPEG image file generator that creates images with rendered text."""

from pathlib import Path
from typing import Any, Union

from PIL import Image, ImageDraw  # noqa: F401 - Used indirectly

from ...generators.base import FileGenerator
from ...generators.registration import register_generator
from ...utils.file_utils import ensure_directory
from ...utils.image_utils import (
    create_blank_image,
    draw_text_on_image,
    load_font,
    save_image,
)
from ...validators.base import ValidationResult  # noqa: F401 - Type hints

# Default font sizes for different content lengths
FONT_SIZES = {
    "small": (100, 36),  # For 1-50 chars
    "medium": (200, 48),  # For 51-200 chars
    "large": (300, 60),  # For 201-500 chars
    "xlarge": (400, 72),  # For 500+ chars
}

DEFAULT_BG_COLOR = "#f0f0f0"
DEFAULT_TEXT_COLOR = "#333333"
DEFAULT_PADDING = 40


def generate_jpg(
    content: str,
    output_path: Path,
    **kwargs: Any,
) -> Path:
    """Generate a JPEG image with the given content rendered as text.

    Args:
        content: The text content to render in the image
        output_path: Path where the JPEG file should be created
        **kwargs: Additional keyword arguments:
            - size: Tuple of (width, height) in pixels (default: auto-calculated)
            - bg_color: Background color (name or hex code, default: '#f0f0f0')
            - text_color: Text color (name or hex code, default: '#333333')
            - font_path: Path to a .ttf or .otf font file (default: system font)
            - font_size: Font size in points (default: auto-calculated)
            - padding: Padding around the text in pixels (default: 40)
            - align: Text alignment ('left', 'center', 'right', default: 'center')
            - valign: Vertical alignment ('top', 'middle', 'bottom', default: 'middle')
            - quality: JPEG quality (1-100, default: 85)
            - optimize: Whether to optimize the JPEG (default: True)
            - progressive: Whether to save as progressive JPEG (default: True)
            - shadow: Whether to add a shadow to the text (default: False)
            - border: Whether to add a border around the text (default: False)
            - border_color: Border color (name or hex code, default: '#000000')
            - border_width: Border width in pixels (default: 1)
            - shadow_color: Shadow color (name or hex code with alpha,
                default: '#00000080')
            - shadow_offset: (x, y) offset for the shadow (default: (2, 2))
            - line_spacing: Space between lines in pixels (default: 4)
            - max_width: Maximum width for text wrapping (default: 80% of
                image width)
            - auto_resize: Whether to automatically resize the image to fit
                the text (default: True)
            - dpi: DPI for the image (default: 72)

    Returns:
        Path to the generated JPEG file

    Raises:
        OSError: If the file cannot be written
        ValueError: If the content is empty or invalid
    """
    if not content or not isinstance(content, str):
        raise ValueError("Content must be a non-empty string")

    output_path = Path(output_path)
    ensure_directory(output_path.parent)

    # Get options with defaults
    size = kwargs.get("size")
    bg_color = kwargs.get("bg_color", DEFAULT_BG_COLOR)
    text_color = kwargs.get("text_color", DEFAULT_TEXT_COLOR)
    font_path = kwargs.get("font_path")
    font_size = kwargs.get("font_size")
    padding = kwargs.get("padding", DEFAULT_PADDING)
    align = kwargs.get("align", "center")
    valign = kwargs.get("valign", "middle")
    quality = max(1, min(100, int(kwargs.get("quality", 85))))
    optimize = bool(kwargs.get("optimize", True))
    progressive = bool(kwargs.get("progressive", True))
    shadow = bool(kwargs.get("shadow", False))
    border = bool(kwargs.get("border", False))
    border_color = kwargs.get("border_color", "#000000")
    border_width = max(1, int(kwargs.get("border_width", 1)))
    shadow_color = kwargs.get("shadow_color", "#00000080")
    shadow_offset = kwargs.get("shadow_offset", (2, 2))
    line_spacing = max(0, int(kwargs.get("line_spacing", 4)))
    max_width = kwargs.get("max_width")
    auto_resize = bool(kwargs.get("auto_resize", True))
    dpi = max(1, int(kwargs.get("dpi", 72)))

    # Calculate default size based on content length if not provided
    if size is None:
        content_length = len(content)
        if content_length <= 50:
            size = FONT_SIZES["small"]
        elif content_length <= 200:
            size = FONT_SIZES["medium"]
        elif content_length <= 500:
            size = FONT_SIZES["large"]
        else:
            size = FONT_SIZES["xlarge"]

    # Ensure size is a tuple of integers
    width, height = map(int, size)

    # Calculate max width for text wrapping if not provided
    if max_width is None and auto_resize:
        max_width = int(width * 0.8)  # 80% of image width

    # Create a temporary image to calculate text dimensions
    temp_img = create_blank_image(width, height, bg_color)
    # ImageDraw is used indirectly by draw_text_on_image
    _ = ImageDraw.Draw(temp_img)  # noqa: F841 - Used for text measurement

    # Load font with default size if not specified
    if font_size is None:
        # Start with a default font size and adjust based on content
        font_size = 24
        if len(content) > 500:
            font_size = 16
        elif len(content) > 200:
            font_size = 20
        elif len(content) > 50:
            font_size = 24
        else:
            font_size = 36

    _ = load_font(font_path, font_size)  # noqa: F841 - Used in get_text_dimensions

    # Calculate text dimensions with wrapping
    def get_text_dimensions(text, font, max_width=None):
        """Calculate the dimensions of the text with wrapping."""
        if not text:
            return (0, 0)  # Fix linting issue: consistent return types

        # Handle multi-line text
        if "\n" in text or (max_width and font.getlength(text) > max_width):
            # Simple word wrapping
            lines = []
            for line in text.split("\n"):
                if not line.strip():
                    lines.append("")
                    continue

                if max_width:
                    words = line.split(" ")
                    current_line = []

                    for word in words:
                        # Test if adding this word would exceed the max width
                        test_line = " ".join(current_line + [word])
                        if font.getlength(test_line) <= max_width:
                            current_line.append(word)
                        else:
                            if current_line:
                                lines.append(" ".join(current_line))
                            current_line = [word]

                    # Add the last line
                    if current_line:
                        lines.append(" ".join(current_line))
                else:
                    lines.append(line)

                # Calculate total height and max width
                total_height = 0
                max_line_width = 0
                line_heights = []

                for line in lines:
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]  # right - left
                    line_height = bbox[3] - bbox[1]  # bottom - top

                    max_line_width = max(max_line_width, line_width)
                    line_heights.append(line_height)
                    total_height += line_height + line_spacing

                # Remove extra spacing after last line
                if lines:
                    total_height -= line_spacing

                return (max_line_width, total_height)
            else:
                # Single line of text
                bbox = font.getbbox(text)
                return (bbox[2] - bbox[0], bbox[3] - bbox[1])

        # Get text dimensions
        text_width, text_height = get_text_dimensions(content, font, max_width)

        # Initialize width and height if not already set
        if "width" not in locals():
            width = 800  # Default width if not set
        if "height" not in locals():
            height = 600  # Default height if not set

        # Adjust image size if auto_resize is True and text doesn't fit
        if auto_resize:
            # Add padding
            required_width = text_width + 2 * padding
            required_height = text_height + 2 * padding

            # Ensure minimum size
            min_width, min_height = 100, 50
            required_width = max(required_width, min_width)
            required_height = max(required_height, min_height)

            # Only resize if needed
            if required_width > width or required_height > height:
                width = max(width, required_width)
                height = max(height, required_height)

        # Create the actual image
        img = create_blank_image(width, height, bg_color)

        # Calculate text position based on alignment
        x = width // 2  # Default to center
        y = height // 2  # Default to middle

        # Draw the text
        img = draw_text_on_image(
            image=img,
            text=content,
            position=(x, y),
            font=font,
            color=text_color,
            bg_color=bg_color if border else None,
            align=align,
            valign=valign,
            padding=padding,
            shadow=shadow,
            shadow_color=shadow_color,
            shadow_offset=shadow_offset,
            border=border,
            border_color=border_color,
            border_width=border_width,
        )

        # Save the image
        save_image(
            img,
            output_path,
            format="JPEG",
            quality=quality,
            optimize=optimize,
            progressive=progressive,
            dpi=(dpi, dpi),
        )

        return output_path


class JpgGenerator(FileGenerator):
    """Generator for JPG image files."""

    @classmethod
    def generate(cls, content: str, output_path: Path, **kwargs: Any) -> Path:
        """Generate a JPG file with the given content.

        Args:
            content: The text content to include in the image
            output_path: Path where the JPG file should be saved
            **kwargs: Additional keyword arguments (see generate_jpg for details)

        Returns:
            Path to the generated JPG file
        """
        return generate_jpg(content, output_path, **kwargs)

    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> "ValidationResult":
        """Validate that the file is a valid JPEG image.

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is a valid JPEG
        """
        from ...validators.image_validator import JpegValidator

        return JpegValidator.validate(file_path)


# Register the generator
@register_generator(["jpg", "jpeg"])
def generate_jpg_file(
    content: str,
    output_path: Path,
    **kwargs: Any,
) -> Path:
    """Generate a JPG file with the given content.

    Args:
        content: The text content to include in the image
        output_path: Path where the JPG file should be saved
        **kwargs: Additional keyword arguments:
            - size: Tuple of (width, height) in pixels (default: auto-calculated)
            - bg_color: Background color (name or hex code, default: '#f0f0f0')
            - text_color: Text color (name or hex code, default: '#333333')
            - font_path: Path to a .ttf or .otf font file (default: system font)
            - font_size: Font size in points (default: auto-calculated)
            - padding: Padding around the text in pixels (default: 40)
            - quality: JPEG quality (1-100, default: 85)
            - optimize: Whether to optimize the JPEG (default: True)
            - progressive: Whether to save as progressive JPEG (default: True)
            - shadow: Whether to add a shadow to the text (default: False)
            - border: Whether to add a border around the text (default: False)

    Returns:
        Path: The path to the generated JPG file
    """
    return generate_jpg(content, output_path, **kwargs)
