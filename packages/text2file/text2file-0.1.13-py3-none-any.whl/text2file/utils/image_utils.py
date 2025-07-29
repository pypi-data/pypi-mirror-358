"""Utility functions for image operations."""

import base64
import io
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

from .file_utils import ensure_directory


def create_blank_image(
    width: int = 800,
    height: int = 600,
    color: str = "#FFFFFF",
    mode: str = "RGB"
) -> Image.Image:
    """Create a new blank image.

    Args:
        width: Width of the image in pixels
        height: Height of the image in pixels
        color: Background color (name or hex code)
        mode: Image mode (e.g., 'RGB', 'RGBA', 'L')

    Returns:
        A new PIL Image object
    """
    try:
        # Try to parse the color
        bg_color = ImageColor.getrgb(color)
        # If the mode is RGBA, ensure we have 4 components
        if mode == "RGBA":
            if len(bg_color) == 3:  # RGB
                bg_color = bg_color + (255,)  # Add full opacity
    except (ValueError, AttributeError):
        # Default to white if color parsing fails
        bg_color = (255, 255, 255) if mode == "RGB" else (255, 255, 255, 255)

    return Image.new(mode, (width, height), color=bg_color)


def load_font(
    font_path: Optional[str] = None,
    font_size: int = 12
) -> ImageFont.FreeTypeFont:
    """Load a font with fallback to default system font.

    Args:
        font_path: Path to a .ttf or .otf font file
        font_size: Font size in points

    Returns:
        A PIL ImageFont object
    """
    try:
        if font_path:
            return ImageFont.truetype(font_path, font_size)

        # Try to find a default system font
        try:
            # Try to use a common system font
            return ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            try:
                # Try another common font
                return ImageFont.truetype("DejaVuSans.ttf", font_size)
            except IOError:
                # Fall back to default font
                return ImageFont.load_default()
    except Exception:
        # Last resort
        return ImageFont.load_default()


def get_text_size(
    text: str,
    font: ImageFont.FreeTypeFont,
    spacing: int = 4,
    max_width: Optional[int] = None,
) -> Tuple[int, int]:
    """Calculate the size of text when rendered with the given font.

    Args:
        text: Text to measure
        font: PIL ImageFont object
        spacing: Line spacing (only used for multiline text)
        max_width: Maximum width for text wrapping (pixels)

    Returns:
        Tuple of (width, height) in pixels
    """
    if not text:
        return (0, 0)

    # Handle multiline text
    if "\n" in text or (max_width and font.getlength(text) > max_width):
        return get_multiline_text_size(text, font, spacing, max_width)

    # Single line of text
    left, top, right, bottom = font.getbbox(text)
    return (right - left, bottom - top)


def get_multiline_text_size(
    text: str,
    font: ImageFont.FreeTypeFont,
    spacing: int = 4,
    max_width: Optional[int] = None,
) -> Tuple[int, int]:
    """Calculate the size of multiline text when rendered with the given font.

    Args:
        text: Text to measure (can contain newlines)
        font: PIL ImageFont object
        spacing: Line spacing in pixels
        max_width: Maximum width for text wrapping (pixels)

    Returns:
        Tuple of (width, height) in pixels
    """
    if not text:
        return (0, 0)

    # Split text into lines
    lines = text.split("\n")

    # Process each line, handling word wrapping if max_width is specified
    processed_lines = []
    for line in lines:
        if not line.strip():
            processed_lines.append("")
            continue

        if max_width:
            # Simple word wrapping
            words = line.split(" ")
            current_line = []

            for word in words:
                # Test if adding this word would exceed the max width
                test_line = " ".join(current_line + [word])
                if font.getlength(test_line) <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        processed_lines.append(" ".join(current_line))
                    current_line = [word]

            # Add the last line
            if current_line:
                processed_lines.append(" ".join(current_line))
        else:
            processed_lines.append(line)

    # Calculate total height and max width
    total_height = 0
    max_line_width = 0
    line_heights = []

    for i, line in enumerate(processed_lines):
        left, top, right, bottom = font.getbbox(line)
        line_width = right - left
        line_height = bottom - top + (spacing if i < len(processed_lines) - 1 else 0)

        max_line_width = max(max_line_width, line_width)
        line_heights.append(line_height)
        total_height += line_height

    return (max_line_width, total_height)


def draw_text_on_image(
    image: Image.Image,
    text: str,
    position: Tuple[int, int] = (0, 0),
    font: Optional[ImageFont.FreeTypeFont] = None,
    font_size: int = 12,
    font_path: Optional[str] = None,
    color: str = "#000000",
    bg_color: Optional[str] = None,
    align: str = "left",
    valign: str = "top",
    max_width: Optional[int] = None,
    line_spacing: int = 4,
    padding: int = 10,
    rotate: int = 0,
    shadow: bool = False,
    shadow_color: str = "#00000080",
    shadow_offset: Tuple[int, int] = (2, 2),
    border: bool = False,
    border_color: str = "#000000",
    border_width: int = 1,
) -> Image.Image:
    """Draw text on an image with various formatting options.

    Args:
        image: PIL Image to draw on
        text: Text to draw
        position: (x, y) coordinates for the text
        font: Font to use (if None, will be loaded)
        font_size: Font size in points
        font_path: Path to a .ttf or .otf font file
        color: Text color (name or hex code)
        bg_color: Background color (name or hex code), or None for transparent
        align: Horizontal alignment ('left', 'center', 'right')
        valign: Vertical alignment ('top', 'middle', 'bottom')
        max_width: Maximum width for text wrapping (pixels)
        line_spacing: Space between lines in pixels
        padding: Padding around the text
        rotate: Rotation angle in degrees
        shadow: Whether to add a shadow
        shadow_color: Shadow color (name or hex code with alpha)
        shadow_offset: (x, y) offset for the shadow
        border: Whether to add a border around the text
        border_color: Border color (name or hex code)
        border_width: Border width in pixels

    Returns:
        The modified image with text drawn on it
    """
    if not text:
        return image

    # Load font if not provided
    if font is None:
        font = load_font(font_path, font_size)

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Handle multiline text and word wrapping
    lines = []
    if "\n" in text or (max_width and font.getlength(text) > max_width):
        # Split text into lines and handle word wrapping
        lines = []
        for line in text.split("\n"):
            if not line.strip():
                lines.append("")
                continue

            if max_width:
                # Simple word wrapping
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
    else:
        lines = [text]

    # Calculate total text size
    line_heights = []
    max_line_width = 0

    for line in lines:
        left, top, right, bottom = font.getbbox(line)
        line_width = right - left
        line_height = bottom - top

        max_line_width = max(max_line_width, line_width)
        line_heights.append(line_height)

    total_height = sum(line_heights) + (len(lines) - 1) * line_spacing

    # Calculate text position based on alignment
    x, y = position

    # Handle horizontal alignment
    if align == "center":
        x -= max_line_width // 2
    elif align == "right":
        x -= max_line_width

    # Handle vertical alignment
    if valign == "middle":
        y -= total_height // 2
    elif valign == "bottom":
        y -= total_height

    # Draw each line of text
    current_y = y

    for i, line in enumerate(lines):
        line_height = line_heights[i]
        line_left = x

        # Handle horizontal alignment for each line
        if align == "center":
            left, top, right, bottom = font.getbbox(line)
            line_width = right - left
            line_left = x + (max_line_width - line_width) // 2
        elif align == "right":
            left, top, right, bottom = font.getbbox(line)
            line_width = right - left
            line_left = x + (max_line_width - line_width)

        # Draw shadow if enabled
        if shadow:
            shadow_pos = (line_left + shadow_offset[0], current_y + shadow_offset[1])
            draw.text(shadow_pos, line, font=font, fill=shadow_color)

        # Draw border if enabled
        if border and border_width > 0:
            # Draw text multiple times with offset to create a border effect
            for x_offset in [-border_width, 0, border_width]:
                for y_offset in [-border_width, 0, border_width]:
                    if x_offset == 0 and y_offset == 0:
                        continue  # Skip the center position for the border
                    pos = (line_left + x_offset, current_y + y_offset)
                    draw.text(pos, line, font=font, fill=border_color)

        # Draw the main text
        draw.text((line_left, current_y), line, font=font, fill=color)

        # Move to the next line
        current_y += line_height + line_spacing

    return image


def create_text_image(
    text: str,
    size: Tuple[int, int] = (800, 400),
    bg_color: str = "#FFFFFF",
    text_color: str = "#000000",
    font_size: int = 24,
    font_path: Optional[str] = None,
    align: str = "center",
    valign: str = "middle",
    padding: int = 20,
    rotate: int = 0,
    shadow: bool = False,
    shadow_color: str = "#00000080",
    shadow_offset: Tuple[int, int] = (2, 2),
    border: bool = False,
    border_color: str = "#000000",
    border_width: int = 1,
) -> Image.Image:
    """Create an image with centered text.

    Args:
        text: Text to display
        size: (width, height) of the image
        bg_color: Background color (name or hex code)
        text_color: Text color (name or hex code)
        font_size: Font size in points
        font_path: Path to a .ttf or .otf font file
        align: Horizontal alignment ('left', 'center', 'right')
        valign: Vertical alignment ('top', 'middle', 'bottom')
        padding: Padding around the text in pixels
        rotate: Rotation angle in degrees
        shadow: Whether to add a shadow
        shadow_color: Shadow color (name or hex code with alpha)
        shadow_offset: (x, y) offset for the shadow
        border: Whether to add a border around the text
        border_color: Border color (name or hex code)
        border_width: Border width in pixels

    Returns:
        A PIL Image object with the text rendered on it
    """
    # Create a new image with the specified background color
    image = create_blank_image(size[0], size[1], bg_color)

    # Calculate text position (centered)
    x = size[0] // 2
    y = size[1] // 2

    # Draw the text
    image = draw_text_on_image(
        image=image,
        text=text,
        position=(x, y),
        font_size=font_size,
        font_path=font_path,
        color=text_color,
        align=align,
        valign=valign,
        padding=padding,
        rotate=rotate,
        shadow=shadow,
        shadow_color=shadow_color,
        shadow_offset=shadow_offset,
        border=border,
        border_color=border_color,
        border_width=border_width,
    )

    return image


def save_image(
    image: Image.Image,
    output_path: Union[str, Path],
    format: Optional[str] = None,
    quality: int = 95,
    **kwargs,
) -> bool:
    """Save an image to a file with the specified format and quality.

    Args:
        image: PIL Image to save
        output_path: Path to save the image to
        format: Output format (e.g., 'JPEG', 'PNG'). If None, inferred from extension
        quality: Quality setting (1-100, higher is better)
        **kwargs: Additional arguments to pass to Image.save()

    Returns:
        True if the image was saved successfully, False otherwise
    """
    try:
        output_path = Path(output_path)
        ensure_directory(output_path.parent)

        # Determine format from extension if not provided
        if format is None:
            ext = output_path.suffix.lower()
            if ext in [".jpg", ".jpeg", ".jpe", ".jfif", ".jif"]:
                format = "JPEG"
            elif ext == ".png":
                format = "PNG"
            elif ext == ".gif":
                format = "GIF"
            elif ext in [".tif", ".tiff"]:
                format = "TIFF"
            elif ext == ".webp":
                format = "WEBP"
            elif ext == ".bmp":
                format = "BMP"
            else:
                format = "PNG"  # Default to PNG for unknown extensions

        # Handle format-specific options
        save_kwargs = kwargs.copy()

        if format.upper() == "JPEG":
            if image.mode in ("RGBA", "LA"):
                # Convert to RGB for JPEG
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(
                    image, mask=image.split()[-1]
                )  # Paste using alpha channel as mask
                image = background
            save_kwargs.setdefault("quality", quality)
            save_kwargs.setdefault("optimize", True)
            save_kwargs.setdefault("progressive", True)

        elif format.upper() == "PNG":
            save_kwargs.setdefault("optimize", True)
            if "compress_level" not in save_kwargs:
                save_kwargs["compress_level"] = 6  # Default compression level for PNG

        elif format.upper() == "WEBP":
            save_kwargs.setdefault("quality", quality)
            save_kwargs.setdefault(
                "method", 6
            )  # Default method (0=fast, 6=slowest/smallest)

        # Save the image
        image.save(output_path, format=format, **save_kwargs)
        return True

    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def image_to_base64(image: Image.Image, format: str = "PNG", **kwargs) -> str:
    """Convert a PIL Image to a base64-encoded string.

    Args:
        image: PIL Image to convert
        format: Output format (e.g., 'JPEG', 'PNG')
        **kwargs: Additional arguments to pass to Image.save()

    Returns:
        Base64-encoded string representation of the image
    """
    buffered = io.BytesIO()
    image.save(buffered, format=format, **kwargs)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def base64_to_image(data: str) -> Optional[Image.Image]:
    """Convert a base64-encoded string to a PIL Image.

    Args:
        data: Base64-encoded image data

    Returns:
        PIL Image, or None if conversion failed
    """
    try:
        if "," in data:
            # Handle data URLs (e.g., 'data:image/png;base64,...')
            data = data.split(",", 1)[1]
        return Image.open(io.BytesIO(base64.b64decode(data)))
    except Exception:
        return None


def resize_image(
    image: Image.Image,
    size: Tuple[int, int],
    resample: int = Image.Resampling.LANCZOS,
    keep_aspect_ratio: bool = True,
    bg_color: str = "#FFFFFF",
) -> Image.Image:
    """Resize an image while optionally maintaining aspect ratio.

    Args:
        image: PIL Image to resize
        size: Target size as (width, height)
        resample: Resampling filter to use (from PIL.Image.Resampling)
        keep_aspect_ratio: Whether to maintain the aspect ratio
        bg_color: Background color if aspect ratio is maintained

    Returns:
        Resized PIL Image
    """
    if not keep_aspect_ratio:
        return image.resize(size, resample=resample)

    # Calculate aspect ratio
    orig_width, orig_height = image.size
    target_width, target_height = size

    # Calculate new dimensions maintaining aspect ratio
    width_ratio = target_width / orig_width
    height_ratio = target_height / orig_height

    if width_ratio < height_ratio:
        # Fit to width
        new_width = target_width
        new_height = int(orig_height * width_ratio)
    else:
        # Fit to height
        new_height = target_height
        new_width = int(orig_width * height_ratio)

    # Resize the image
    resized_image = image.resize((new_width, new_height), resample=resample)

    # If the aspect ratio is different, create a new image with the target size and paste
    if new_width != target_width or new_height != target_height:
        result = create_blank_image(target_width, target_height, bg_color, "RGBA")
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        result.paste(resized_image, (x, y))
        return result

    return resized_image


def apply_filter(
    image: Image.Image,
    filter_name: str,
    **kwargs
) -> Optional[Image.Image]:
    """Apply a filter to an image.

    Args:
        image: PIL Image to filter
        filter_name: Name of the filter to apply
        **kwargs: Additional arguments for the filter

    Returns:
        Filtered PIL Image
    """
    filter_name = filter_name.lower()

    if filter_name == "blur":
        radius = kwargs.get("radius", 2)
        return image.filter(ImageFilter.GaussianBlur(radius))

    elif filter_name == "sharpen":
        return image.filter(ImageFilter.SHARPEN)

    elif filter_name == "edge_enhance":
        return image.filter(ImageFilter.EDGE_ENHANCE)

    elif filter_name == "emboss":
        return image.filter(ImageFilter.EMBOSS)

    elif filter_name == "contour":
        return image.filter(ImageFilter.CONTOUR)

    elif filter_name == "detail":
        return image.filter(ImageFilter.DETAIL)

    elif filter_name == "smooth":
        return image.filter(ImageFilter.SMOOTH)

    elif filter_name == "grayscale":
        return image.convert("L")

    elif filter_name == "sepia":
        # Create a sepia tone effect
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Sepia matrix
        sepia_matrix = (0.393, 0.769, 0.189, 0.349, 0.686, 0.168, 0.272, 0.534, 0.131)
        sepia_image = image.convert("RGB", sepia_matrix)
        return sepia_image

    # Add more filters as needed...

    else:
        raise ValueError(f"Unknown filter: {filter_name}")
