"""Validators for video file formats."""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

import cv2  # type: ignore

from .base import BaseValidator, ValidationResult

# Try to import OpenCV for video validation
HAS_OPENCV = False
try:
    import cv2  # noqa: F811
    HAS_OPENCV = True
except ImportError:
    pass

# Try to import ffprobe for more detailed video info
HAS_FFPROBE = bool(
    subprocess.run(
        ["which", "ffprobe"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).returncode == 0
)


class VideoValidator(BaseValidator):
    """Base validator for video files."""

    # Expected format for this validator (should be overridden by subclasses)
    FORMAT: Optional[str] = None

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a video file.

        Args:
            file_path: Path to the video file to validate

        Returns:
            ValidationResult indicating whether the video is valid
        """
        try:
            # First check if the file exists and is readable
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    is_valid=False,
                    message=f"File not found: {file_path}"
                )

            if not path.is_file():
                return ValidationResult(
                    is_valid=False,
                    message=f"Not a file: {file_path}"
                )

            # Check file extension against expected format
            if cls.FORMAT and not file_path.lower().endswith(f".{cls.FORMAT}"):
                return ValidationResult(
                    is_valid=False,
                    message=(
                        f"Expected .{cls.FORMAT} file, got "
                        f"{Path(file_path).suffix}"
                    )
                )

            # If all else fails, check if the file is not empty
            if path.stat().st_size == 0:
                return ValidationResult(
                    is_valid=False,
                    message="File is empty"
                )

            # Try to validate with OpenCV first
            if HAS_OPENCV:
                result = cls._validate_with_opencv(file_path)
                if result.is_valid:
                    return result

            # If OpenCV fails or is not available, try ffprobe
            if HAS_FFPROBE:
                result = cls._validate_with_ffprobe(file_path)
                if result.is_valid:
                    return result

            # If we get here, we couldn't validate the video
            return ValidationResult(
                is_valid=False,
                message=(
                    "Could not validate video (missing dependencies: "
                    "install OpenCV or ffmpeg)"
                ),
                details={
                    "opencv_available": HAS_OPENCV,
                    "ffprobe_available": HAS_FFPROBE,
                    "size": path.stat().st_size,
                },
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating video file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _validate_with_opencv(cls, file_path: str) -> ValidationResult:
        """Validate a video file using OpenCV."""
        if not HAS_OPENCV:
            return ValidationResult(
                is_valid=False,
                message="OpenCV is not available"
            )

        try:
            # Check file readability first
            if not os.access(file_path, os.R_OK):
                return ValidationResult(
                    is_valid=False,
                    message=f"File not readable: {file_path}"
                )

            # Open the video file
            cap = cv2.VideoCapture(file_path)

            if not cap.isOpened():
                return ValidationResult(
                    is_valid=False, message="Could not open video file with OpenCV"
                )

            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            # Try to read the first frame
            ret, frame = cap.read()
            if not ret:
                return ValidationResult(
                    is_valid=False, message="Could not read any frames from the video"
                )

            # Release the video capture object
            cap.release()

            return ValidationResult(
                is_valid=True,
                message=(
                    f"Valid video: {width}x{height} @ {fps:.2f} fps, "
                    f"{frame_count} frames"
                ),
                details={
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration_seconds": duration,
                    "validated_with": "opencv",
                },
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating with OpenCV: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _validate_with_ffprobe(cls, file_path: str) -> ValidationResult:
        """Validate video file using ffprobe.

        Args:
            file_path: Path to the video file

        Returns:
            ValidationResult indicating if the video is valid
        """
        if not HAS_FFPROBE:
            return ValidationResult(
                is_valid=False,
                message="ffprobe is not available"
            )
            
        try:
            # Run ffprobe to get video information
            result = subprocess.run(
                command=[
                    'ffprobe',
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries',
                    'stream=codec_name,width,height,r_frame_rate,duration,nb_frames',
                    '-show_entries', 'format=format_name,duration,size',
                    '-of', 'json',
                    file_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            # Parse the JSON output
            try:
                info = json.loads(result.stdout)
                if not info:
                    return ValidationResult(
                        is_valid=False,
                        message="No video information found"
                    )
                
                # Check if we have at least one video stream
                if 'streams' not in info or not info['streams']:
                    return ValidationResult(
                        is_valid=False,
                        message="No video streams found"
                    )
                
                format_name = info.get('format', {}).get('format_name', 'unknown')
                return ValidationResult(
                    is_valid=True,
                    message=f"Video is valid: {format_name}"
                )

            except json.JSONDecodeError:
                return ValidationResult(
                    is_valid=False,
                    message="Invalid JSON output from ffprobe"
                )

            # If we get here, something went wrong
            return ValidationResult(
                is_valid=False,
                message="Unknown validation error occurred"
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating with ffprobe: {str(e)}",
                details={"error": str(e)},
            )


class Mp4Validator(VideoValidator):
    """Validator for MP4 video files."""

    FORMAT = "mp4"


class AviValidator(VideoValidator):
    """Validator for AVI video files."""

    FORMAT = "avi"


class MovValidator(VideoValidator):
    """Validator for QuickTime MOV video files."""

    FORMAT = "mov"


class MkvValidator(VideoValidator):
    """Validator for Matroska MKV video files."""

    FORMAT = "mkv"


class WebmValidator(VideoValidator):
    """Validator for WebM video files."""

    FORMAT = "webm"


class FlvValidator(VideoValidator):
    """Validator for Flash Video FLV files."""

    FORMAT = "flv"


class WmvValidator(VideoValidator):
    """Validator for Windows Media Video WMV files."""

    FORMAT = "wmv"


class MpegValidator(VideoValidator):
    """Validator for MPEG video files."""

    FORMAT = "mpeg"


class M4vValidator(VideoValidator):
    """Validator for M4V video files."""

    FORMAT = "m4v"


class ThreeGpValidator(VideoValidator):
    """Validator for 3GP video files."""

    FORMAT = "3gp"


class MtsValidator(VideoValidator):
    """Validator for MTS video files (AVCHD)."""

    FORMAT = "mts"


class M2tsValidator(VideoValidator):
    """Validator for M2TS video files (Blu-ray)."""

    FORMAT = "m2ts"


class VobValidator(VideoValidator):
    """Validator for VOB video files (DVD)."""

    FORMAT = "vob"


class AsfValidator(VideoValidator):
    """Validator for ASF video files."""

    FORMAT = "asf"


class SwfValidator(VideoValidator):
    """Validator for SWF (Shockwave Flash) files."""

    FORMAT = "swf"


class MpgValidator(VideoValidator):
    """Validator for MPG video files."""

    FORMAT = "mpg"


class MpeValidator(VideoValidator):
    """Validator for MPE video files."""

    FORMAT = "mpe"


class M2vValidator(VideoValidator):
    """Validator for M2V video files."""

    FORMAT = "m2v"


class TsValidator(VideoValidator):
    """Validator for TS (MPEG Transport Stream) video files."""

    FORMAT = "ts"


class MxfValidator(VideoValidator):
    """Validator for MXF video files."""

    FORMAT = "mxf"


class OggValidator(VideoValidator):
    """Validator for OGG video files."""

    FORMAT = "ogg"


class OgvValidator(VideoValidator):
    """Validator for OGV video files."""

    FORMAT = "ogv"


class F4vValidator(VideoValidator):
    """Validator for F4V video files."""

    FORMAT = "f4v"


class MjpegValidator(VideoValidator):
    """Validator for MJPEG video files."""

    FORMAT = "mjpeg"


class Mj2Validator(VideoValidator):
    """Validator for MJ2 video files."""

    FORMAT = "mj2"


class DvValidator(VideoValidator):
    """Validator for DV video files."""

    FORMAT = "dv"


class H261Validator(VideoValidator):
    """Validator for H.261 video files."""

    FORMAT = "h261"


class H263Validator(VideoValidator):
    """Validator for H.263 video files."""

    FORMAT = "h263"


class H264Validator(VideoValidator):
    """Validator for H.264 video files."""

    FORMAT = "h264"


class H265Validator(VideoValidator):
    """Validator for H.265/HEVC video files."""

    FORMAT = "h265"


class HevcValidator(VideoValidator):
    """Validator for HEVC video files (same as H.265)."""

    FORMAT = "hevc"


class Vp8Validator(VideoValidator):
    """Validator for VP8 video files."""

    FORMAT = "vp8"


class Vp9Validator(VideoValidator):
    """Validator for VP9 video files."""

    FORMAT = "vp9"


class Av1Validator(VideoValidator):
    """Validator for AV1 video files."""

    FORMAT = "av1"


class TheoraValidator(VideoValidator):
    """Validator for Theora video files."""

    FORMAT = "ogv"  # Theora is typically in OGV/OGG containers


class ProresValidator(VideoValidator):
    """Validator for Apple ProRes video files."""

    FORMAT = "mov"  # ProRes is typically in MOV containers


class DnxhdValidator(VideoValidator):
    """Validator for DNxHD video files."""

    FORMAT = "mxf"  # DNxHD is often in MXF containers


class CineformValidator(VideoValidator):
    """Validator for CineForm video files."""

    FORMAT = "avi"  # CineForm is often in AVI containers


class AnimationValidator(VideoValidator):
    """Validator for Animation video files."""

    FORMAT = "mov"  # Animation codec is typically in MOV containers


class LagarithValidator(VideoValidator):
    """Validator for Lagarith video files."""

    FORMAT = "avi"  # Lagarith is typically in AVI containers


class UtVideoValidator(VideoValidator):
    """Validator for Ut Video files."""

    FORMAT = "avi"  # Ut Video is typically in AVI containers


class HapValidator(VideoValidator):
    """Validator for HAP video files."""

    FORMAT = "mov"  # HAP is typically in MOV containers


class NotchlcValidator(VideoValidator):
    """Validator for NotchLC video files."""

    FORMAT = "mov"  # NotchLC is typically in MOV containers


class SheervideoValidator(VideoValidator):
    """Validator for SheerVideo files."""

    FORMAT = "avi"  # SheerVideo is typically in AVI containers
