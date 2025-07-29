"""Validators for archive file formats."""

import bz2
import gzip
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseValidator, ValidationResult


class ArchiveValidator(BaseValidator):
    """Base validator for archive files."""

    # Expected format for this validator (should be overridden by subclasses)
    FORMAT: Optional[str] = None

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate an archive file.

        Args:
            file_path: Path to the archive file to validate

        Returns:
            ValidationResult indicating whether the archive is valid
        """
        try:
            # First check if the file exists and is readable
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    is_valid=False, message=f"File not found: {file_path}"
                )

            if not path.is_file():
                return ValidationResult(
                    is_valid=False, message=f"Not a file: {file_path}"
                )

            # Check file extension matches expected format
            if cls.FORMAT and not cls._matches_format(path, cls.FORMAT):
                return ValidationResult(
                    is_valid=False,
                    message=(
                        f"Expected {cls.FORMAT.upper()} file, got {path.suffix}"
                    ),
                )

            # Delegate to format-specific validation
            return cls._validate_archive(file_path)

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error processing archive file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _matches_format(cls, path: Path, format_str: str) -> bool:
        """Check if the file extension matches the expected format."""
        if format_str == "tar.gz":
            return (
                path.suffixes == [".tar", ".gz"] or 
                path.suffix == ".tgz"
            )
        if format_str == "tar.bz2":
            return (
                path.suffixes == [".tar", ".bz2"] or 
                path.suffix == ".tbz2"
            )
        return path.suffix.lower() == f".{format_str}"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Perform format-specific archive validation."""
        raise NotImplementedError("Subclasses must implement _validate_archive()")

    @classmethod
    def _get_archive_contents(cls, file_path: str) -> List[Dict[str, Any]]:
        """Get a list of files in the archive with their details."""
        raise NotImplementedError("Subclasses must implement _get_archive_contents()")


class ZipValidator(ArchiveValidator):
    """Validator for ZIP archives."""

    FORMAT = "zip"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Validate a ZIP archive."""
        try:
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                # Test the zip file integrity
                test_result = zip_ref.testzip()
                if test_result is not None:
                    return ValidationResult(
                        is_valid=False,
                        message=f"Corrupt file in ZIP archive: {test_result}",
                        details={"corrupt_file": test_result},
                    )

                # Get archive contents
                contents = cls._get_archive_contents(file_path)

                return ValidationResult(
                    is_valid=True,
                    message=f"Valid ZIP archive with {len(contents)} files",
                    details={
                        "file_count": len(contents),
                        "total_size": sum(f["size"] for f in contents),
                        "files": contents,
                    },
                )

        except zipfile.BadZipFile as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid ZIP file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _get_archive_contents(cls, file_path: str) -> List[Dict[str, Any]]:
        """Get a list of files in the ZIP archive with their details.
        
        Args:
            file_path: Path to the archive file
            
        Returns:
            List of dictionaries containing file information
        """
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            return [
                {
                    'filename': info.filename,
                    'file_size': info.file_size,
                    'compress_size': info.compress_size,
                    'is_dir': info.is_dir(),
                    'modified': info.date_time,
                }
                for info in zip_ref.infolist()
            ]


class TarValidator(ArchiveValidator):
    """Validator for tar archives."""

    FORMAT = "tar"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Validate a tar archive."""
        try:
            with tarfile.open(file_path, "r:*") as tar_ref:
                # This will raise an exception if the tar is corrupted
                tar_members = tar_ref.getmembers()

                # Get archive contents
                contents = cls._get_archive_contents(file_path)

                return ValidationResult(
                    is_valid=True,
                    message=f"Valid TAR archive with {len(contents)} files",
                    details={
                        "file_count": len(contents),
                        "total_size": sum(f["size"] for f in contents),
                        "files": contents,
                    },
                )

        except tarfile.TarError as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid TAR file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _get_archive_contents(cls, file_path: str) -> List[Dict[str, Any]]:
        """Get a list of files in the TAR archive with their details."""
        contents = []
        with tarfile.open(file_path, "r:*") as tar_ref:
            for member in tar_ref.getmembers():
                contents.append(
                    {
                        "filename": member.name,
                        "size": member.size,
                        "modified": member.mtime,
                        "is_dir": member.isdir(),
                        "mode": member.mode,
                        "user": member.uname if hasattr(member, "uname") else "",
                        "group": member.gname if hasattr(member, "gname") else "",
                    }
                )
        return contents


class TarGzValidator(TarValidator):
    """Validator for tar.gz archives."""

    FORMAT = "tar.gz"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Validate a tar.gz archive."""
        # First check if the file is a valid gzip file
        try:
            with gzip.open(file_path, "rb") as f:
                # Try to read a small amount to test the gzip integrity
                f.read(1)
        except (gzip.BadGzipFile, OSError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid gzip file: {str(e)}",
                details={"error": str(e)},
            )

        # Then validate as a tar file
        return super()._validate_archive(file_path)


class TarBz2Validator(TarValidator):
    """Validator for tar.bz2 archives."""

    FORMAT = "tar.bz2"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Validate a tar.bz2 archive."""
        # First check if the file is a valid bzip2 file
        try:
            with bz2.open(file_path, "rb") as f:
                # Try to read a small amount to test the bzip2 integrity
                f.read(1)
        except (OSError, EOFError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid bzip2 file: {str(e)}",
                details={"error": str(e)},
            )

        # Then validate as a tar file
        return super()._validate_archive(file_path)


class GzipValidator(ArchiveValidator):
    """Validator for gzip files."""

    FORMAT = "gz"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Validate a gzip file."""
        try:
            with gzip.open(file_path, "rb") as f:
                # Try to read a small amount to test the gzip integrity
                f.read(1)

            # Get original filename if available
            with gzip.open(file_path, "rb") as f:
                original_filename = f.name

            return ValidationResult(
                is_valid=True,
                message="Valid gzip file",
                details={
                    "original_filename": original_filename
                    if original_filename != file_path
                    else None,
                    "size": Path(file_path).stat().st_size,
                },
            )

        except (gzip.BadGzipFile, OSError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid gzip file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _get_archive_contents(cls, file_path: str) -> List[Dict[str, Any]]:
        """Get information about the gzipped file."""
        return [
            {
                "filename": Path(file_path).name,
                "size": Path(file_path).stat().st_size,
                "is_dir": False,
            }
        ]


class Bzip2Validator(ArchiveValidator):
    """Validator for bzip2 files."""

    FORMAT = "bz2"

    @classmethod
    def _validate_archive(cls, file_path: str) -> ValidationResult:
        """Validate a bzip2 file."""
        try:
            with bz2.open(file_path, "rb") as f:
                # Try to read a small amount to test the bzip2 integrity
                f.read(1)

            return ValidationResult(
                is_valid=True,
                message="Valid bzip2 file",
                details={"size": Path(file_path).stat().st_size},
            )

        except (OSError, EOFError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid bzip2 file: {str(e)}",
                details={"error": str(e)},
            )

    @classmethod
    def _get_archive_contents(cls, file_path: str) -> List[Dict[str, Any]]:
        """Get information about the bzipped file."""
        return [
            {
                "filename": Path(file_path).name,
                "size": Path(file_path).stat().st_size,
                "is_dir": False,
            }
        ]
