"""Generators for image file formats."""

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from ..generators import register_generator


def get_text_dimensions(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont
) -> Tuple[int, int]:
    """Calculate text dimensions using getbbox method.

    Args:
        draw: ImageDraw instance
        text: Text to measure
        font: Font to use for measurement

    Returns:
        tuple: (width, height) of the text bounding box
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]  # width, height


def get_system_font(size: int = 24) -> ImageFont.FreeTypeFont:
    """Try to get a nice system font, fall back to default if not available."""
    try:
        # Try to use DejaVuSans or Arial, fall back to default
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except IOError:
            try:
                return ImageFont.truetype("Arial.ttf", size)
            except IOError:
                return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def create_text_image(
    content: str,
    width: int = 800,
    height: int = 400,
    bg_color: str = "#f0f0f0",
    text_color: str = "#333333",
    font_size: int = 24,
    padding: int = 40,
) -> Image.Image:
    """Create an image with the given text content.

    Args:
        content: Text to display in the image
        width: Width of the output image
        height: Height of the output image
        bg_color: Background color (hex or color name)
        text_color: Text color (hex or color name)
        font_size: Font size in points
        padding: Padding around the text in pixels

    Returns:
        PIL Image object
    """
    # Create a new image with the specified background color
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Try to use a nice font, fall back to default if not available
    try:
        # Try to use DejaVuSans or Arial, fall back to default
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Calculate text position with padding
    text_bbox = draw.textbbox((0, 0), content, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate position to center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text
    draw.text((x, y), content, fill=text_color, font=font)
    return image


@register_generator(["jpg", "jpeg", "png", "bmp", "gif"])
def generate_image_file(content: str, output_path: Path) -> Path:
    """Generate an image file with the given content.

    Args:
        content: Text content to display in the image
        output_path: Path where the image should be saved

    Returns:
        Path to the generated image file

    Raises:
        ValueError: If the image format is not supported
        IOError: If there's an error saving the image
    """
    try:
        # Create an image with the text
        image = create_text_image(
            content=content,
            width=800,
            height=400,
            bg_color="#f8f9fa",  # Light gray background
            text_color="#2c3e50",  # Dark blue-gray text
            font_size=36,
            padding=40,
        )

        # Save the image in the appropriate format
        image_format = output_path.suffix[1:].upper()
        if image_format == "JPG":
            image_format = "JPEG"

        # For PNG, use RGBA mode to support transparency
        if image_format == "PNG":
            image = image.convert("RGBA")

        image.save(output_path, format=image_format, quality=95)
        return output_path

    except KeyError as e:
        raise ValueError(f"Unsupported image format: {output_path.suffix}") from e
    except Exception as e:
        raise IOError(f"Error generating image: {str(e)}") from e
