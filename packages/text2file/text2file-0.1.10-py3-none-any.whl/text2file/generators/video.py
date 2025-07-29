"""Video file generation functionality.

This module provides functions to generate video files with text content.
It supports multiple video formats and can use either ffmpeg or moviepy as the backend.
"""

"""Video file generation functionality.

This module provides functions to generate video files with text content.
It supports multiple video formats and can use either ffmpeg or moviepy as the backend.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

# Only import these when type checking to avoid circular imports
if TYPE_CHECKING:
    from PIL import Image, ImageDraw, ImageFont  # noqa: F401
    from moviepy.editor import TextClip  # noqa: F401
    from ..registration import register_generator  # noqa: F401

# Initialize module-level variables
PILLOW_AVAILABLE = False
NUMPY_AVAILABLE = False
MOVIEPY_AVAILABLE = False
REGISTRATION_AVAILABLE = False

# Initialize module-level imports with type hints
FreeTypeFont: Any = None  # type: ignore
Image: Any = None  # type: ignore
ImageDraw: Any = None  # type: ignore
ImageFont: Any = None  # type: ignore
np: Any = None  # type: ignore
TextClip: Any = None  # type: ignore
CompositeVideoClip: Any = None  # type: ignore
ImageClip: Any = None  # type: ignore
register_generator: Any = None  # type: ignore

# Third-party imports (make optional with try/except)
try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
    from PIL.ImageFont import FreeTypeFont  # type: ignore
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import numpy as np  # type: ignore
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from moviepy.editor import TextClip, CompositeVideoClip, ImageClip  # type: ignore
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    from ..registration import register_generator  # type: ignore
    REGISTRATION_AVAILABLE = True
except ImportError:
    REGISTRATION_AVAILABLE = False


def _create_video_frame(
    text: str,
    width: int = 640,
    height: int = 480,
    bg_color: str = "#000000",
    text_color: str = "#FFFFFF",
    font_size: int = 24,
) -> Any:  # Return type should be PIL.Image.Image but we use Any for optional deps
    """Create a video frame with centered text.
    
    Args:
        text: The text to display on the frame
        width: Frame width in pixels
        height: Frame height in pixels
        bg_color: Background color as hex string
        text_color: Text color as hex string
        font_size: Font size in points
        
    Returns:
        PIL Image object with the rendered frame
    """
    if not PILLOW_AVAILABLE or not NUMPY_AVAILABLE:
        raise ImportError(
            "Video generation requires Pillow and NumPy. "
            "Install with: pip install pillow numpy\n"
            "For additional video format support, install moviepy and ffmpeg:\n"
            "pip install moviepy\n"
            "Note: ffmpeg must be installed separately on your system.\n"
            "See https://ffmpeg.org/ for installation instructions."
        )
    
    # Create a new image with the specified background color
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Try to load a nice font, fall back to default
    font = ImageFont.load_default()
    try:
        font = ImageFont.truetype("Arial.ttf", font_size)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype(
                "LiberationSans-Regular.ttf", font_size
            )
        except (IOError, OSError):
            pass  # Use default font
    
    # Calculate text position (centered)
    if font is not None:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((width - text_width) // 2, (height - text_height) // 2)
        
        # Draw the text
        draw.text(position, text, fill=text_color, font=font)
    
    return image


def _generate_video_with_ffmpeg(
    text: str, output_path: Path, duration: int = 5, fps: int = 24
) -> bool:
    """Generate a video file using ffmpeg.

    This function creates a video by generating individual frames using Pillow
    and then combining them using ffmpeg. It provides better performance and
    more format support compared to the moviepy backend.

    Args:
        text: Text to display in the video. Can contain newlines for multi-line text.
        output_path: Path where the video file will be saved. The extension
                   determines the output format (e.g., .mp4, .avi).
        duration: Duration of the video in seconds. Default is 5 seconds.
        fps: Frames per second. Higher values result in smoother video but larger
            file sizes. Default is 24 fps.

    Returns:
        bool: True if video was generated successfully, False otherwise.

    Raises:
        FileNotFoundError: If ffmpeg is not installed or not in system PATH.
        subprocess.CalledProcessError: If ffmpeg command fails.

    Note:
        Requires ffmpeg to be installed and available in the system PATH.
        Install ffmpeg from https://ffmpeg.org/
    """
    try:
        # Create a temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Create frames using Pillow
            for i in range(duration * fps):
                frame = _create_video_frame(text)
                frame_path = temp_dir_path / f"frame_{i:04d}.png"
                frame.save(frame_path, "PNG")

            # Use ffmpeg to create the video
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-framerate",
                str(fps),
                "-i",
                str(temp_dir_path / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(output_path),
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return True

    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error generating video with ffmpeg: {e}", file=sys.stderr)
        return False


def _generate_video_with_moviepy(
    text: str, output_path: Path, duration: int = 5, fps: int = 24
) -> bool:
    """Generate a video file using moviepy.

    This function creates a simple video with text using the moviepy library.
    It's used as a fallback when ffmpeg is not available.

    Args:
        text: Text to display in the video. Can contain newlines for multi-line text.
        output_path: Path where the video file will be saved. The extension
                   determines the output format (e.g., .mp4, .gif).
        duration: Duration of the video in seconds. Default is 5 seconds.
        fps: Frames per second. Default is 24 fps.

    Returns:
        bool: True if video was generated successfully, False otherwise.

    Note:
        Requires moviepy to be installed. Install with:
        ```
        pip install moviepy
        ```
    """
    try:
        # Create a text clip
        txt_clip = TextClip(
            text,
            fontsize=70,
            color="white",
            size=(1280, 720),
        ).set_duration(duration)

        # Create a color clip for the background
        color_clip = ImageClip(
            _create_video_frame(text).convert("RGB")
        ).set_duration(duration)

        # Overlay the text clip on the color clip
        video = CompositeVideoClip([color_clip, txt_clip])

        # Write the video file
        video.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio=False,
        )
        return True

    except ImportError as e:
        print(f"MoviePy not available: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(
            f"Error generating video with MoviePy: {e}",
            file=sys.stderr,
        )
        return False


def generate_video_file(
    content: str,
    output_path: Union[str, Path],
    duration: int = 5,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    bg_color: str = "black",
    text_color: str = "white",
    font_size: int = 40,
    use_moviepy: bool = False,
) -> bool:
    """Generate a video file with the given text content.
    
    Args:
        content: Text content to display in the video
        output_path: Path where the video file will be saved
        duration: Duration of the video in seconds
        fps: Frames per second
        width: Video width in pixels
        height: Video height in pixels
        bg_color: Background color as a color name or hex string
        text_color: Text color as a color name or hex string
        font_size: Font size in points
        use_moviepy: Whether to use moviepy instead of ffmpeg
        
    Returns:
        bool: True if video was generated successfully, False otherwise
    
    Raises:
        ImportError: If required dependencies are not installed
    """
    if not PILLOW_AVAILABLE or not NUMPY_AVAILABLE:
        raise ImportError(
            "Video generation requires Pillow and NumPy. "
            "Install with: pip install pillow numpy"
        )

    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Try ffmpeg first if not explicitly using moviepy
    if not use_moviepy and _generate_video_with_ffmpeg(
        content, output_path, duration, fps
    ):
        return True

    # Fall back to moviepy if available
    if MOVIEPY_AVAILABLE and _generate_video_with_moviepy(
        content, output_path, duration, fps
    ):
        return True

    error_msg = (
        "Failed to generate video. Make sure you have either moviepy or ffmpeg "
        "installed.\nInstall with: pip install moviepy numpy pillow\n"
        "Or install ffmpeg: https://ffmpeg.org/download.html\n"
        "Video generation failed. Please check that you have ffmpeg installed "
        "and available in your system PATH."
    )
    raise RuntimeError(error_msg)


def _video_not_available(*args, **kwargs):
    """Raise an informative error when video generation is not available.
    
    This function is registered as a placeholder when required dependencies
    are not installed.
    
    Raises:
        ImportError: Always raises with installation instructions.
    """
    raise ImportError(
        "Video generation requires additional dependencies. "
        "Please install them with:\n"
        "pip install opencv-python numpy pillow moviepy"
    )


# Import the registration module if available
try:
    from .registration import register_generator as _register_generator
    register_generator = _register_generator
    REGISTRATION_AVAILABLE = True
except ImportError:
    REGISTRATION_AVAILABLE = False
    # Create a dummy decorator that does nothing
    def _noop_decorator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    register_generator = _noop_decorator
    print("WARNING: Video generator registration is not available. Required dependencies may be missing.", file=sys.stderr)

# Only register the video generator if we have a valid register_generator function
if register_generator is not None and callable(register_generator):
    if all([PILLOW_AVAILABLE, NUMPY_AVAILABLE, MOVIEPY_AVAILABLE]):
        register_generator(["mp4", "avi", "mov", "mkv"])(generate_video_file)
        print("DEBUG: Successfully registered video generator with formats: mp4, avi, mov, mkv")
    else:
        register_generator(["mp4", "avi", "mov", "mkv"])(_video_not_available)
        print("WARNING: Video generator registered with placeholder. Missing dependencies:")
        if not PILLOW_AVAILABLE:
            print("  - Pillow (PIL)")
        if not NUMPY_AVAILABLE:
            print("  - NumPy")
        if not MOVIEPY_AVAILABLE:
            print("  - MoviePy")
else:
    print("WARNING: Could not register video generator. Required dependencies may be missing.", file=sys.stderr)
