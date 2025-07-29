"""Generator for creating sets of images based on JSON configuration."""

import json
import os
from pathlib import Path
from typing import List, Optional, TypedDict, Union

from PIL import Image, ImageDraw, ImageFont

from .base import BaseGenerator


class ImageConfig(TypedDict):
    """Type definition for image configuration."""

    src: str
    sizes: str


class ImageSetConfig(TypedDict):
    """Type definition for the image set configuration."""

    icons: List[ImageConfig]


class ImageSetGenerator(BaseGenerator):
    """Generator for creating sets of images based on JSON configuration."""

    @classmethod
    def generate(
        cls,
        config_path: Union[str, Path],
        output_dir: Union[str, Path],
        base_image: Optional[Union[str, Path]] = None,
        background_color: str = "#ffffff",
        text_color: str = "#000000",
        text: Optional[str] = None,
    ) -> List[Path]:
        """Generate a set of images based on the provided JSON configuration.

        Args:
            config_path: Path to the JSON configuration file
            output_dir: Directory where generated images will be saved
            base_image: Optional base image to use for generation
            background_color: Background color for generated images (if no base image)
            text_color: Text color for generated images (if no base image)
            text: Text to render on the image (if no base image)

        Returns:
            List of paths to generated image files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load and validate the configuration
        with open(config_path, "r", encoding="utf-8") as f:
            config: ImageSetConfig = json.load(f)

        generated_files: List[Path] = []

        for icon in config.get("icons", []):
            try:
                # Parse dimensions (e.g., "100x200" -> (100, 200))
                width, height = map(int, icon["sizes"].lower().split("x"))
                output_path = output_dir / icon["src"]
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Create the image
                if base_image and os.path.exists(base_image):
                    # Resize the base image
                    with Image.open(base_image) as img:
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                        img.save(output_path)
                else:
                    # Create a simple placeholder image
                    img = Image.new("RGB", (width, height), color=background_color)
                    if text:
                        draw = ImageDraw.Draw(img)
                        try:
                            # Try to load a font
                            font_size = min(width, height) // 4
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except IOError:
                            # Fallback to default font
                            font = ImageFont.load_default()

                        # Calculate text position (centered)
                        text_bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        position = (
                            (width - text_width) // 2,
                            (height - text_height) // 2,
                        )

                        draw.text(position, text, fill=text_color, font=font)
                    img.save(output_path)

                generated_files.append(output_path)

            except Exception as e:
                print(f"Error generating {icon.get('src')}: {str(e)}")
                continue

        return generated_files
