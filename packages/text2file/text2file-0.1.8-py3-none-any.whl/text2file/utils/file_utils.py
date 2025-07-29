"""Utility functions for file operations."""

import hashlib
import mimetypes
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def get_file_extension(filename: str) -> str:
    """Get the lowercase file extension without the dot.

    Args:
        filename: The filename or path

    Returns:
        The file extension in lowercase, or an empty string if no extension
    """
    return Path(filename).suffix.lstrip(".").lower()


def get_mime_type(
    file_path: Union[str, Path]
) -> Tuple[Optional[str], Optional[str]]:
    """Get the MIME type of a file.

    Args:
        file_path: Path to the file

    Returns:
        A tuple of (mime_type, encoding)
    """
    return mimetypes.guess_type(str(file_path))


def is_binary_file(
    file_path: Union[str, Path],
    chunk_size: int = 1024
) -> bool:
    """Check if a file is binary.

    Args:
        file_path: Path to the file
        chunk_size: Number of bytes to read for checking

    Returns:
        True if the file appears to be binary, False otherwise
    """
    file_path = Path(file_path)

    # Common binary file extensions (faster than reading content)
    binary_extensions = {
        # Images
        *"jpg jpeg png gif bmp tiff webp ico psd svg".split(),
        # Archives
        *"zip tar gz bz2 7z rar xz z lz lzma lzo".split(),
        # Documents
        *"pdf doc docx xls xlsx ppt pptx odt ods odp".split(),
        # Audio/Video
        *"mp3 wav ogg flac aac wma m4a mp4 avi mkv mov wmv flv webm m4v 3gp"
        .split(),
        "mpg",
        "mpeg",
        "m2ts",
        "mts",
        # Executables
        "exe",
        "dll",
        "so",
        "dylib",
        "class",
        "jar",
        "war",
        "ear",
        "apk",
        "app",
        # Data
        "db",
        "sqlite",
        "sqlite3",
        "mdb",
        "accdb",
        "frm",
        "myd",
        "myi",
        "ibd",
        # Other
        "dat",
        "bin",
        "iso",
        "dmg",
        "img",
        "toast",
        "vcd",
        "msi",
        "msm",
        "msp",
    }

    ext = get_file_extension(file_path)
    if ext in binary_extensions:
        return True

    # For files without extensions or with unknown extensions, check the content
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(chunk_size)
            # Check for null bytes which typically indicate a binary file
            if b"\x00" in chunk:
                return True

            # Try to decode as text
            try:
                chunk.decode("utf-8")
            except UnicodeDecodeError:
                return True

    except (IOError, OSError):
        pass

    return False


def get_file_hash(
    file_path: Union[str, Path],
    algorithm: str = "sha256",
    chunk_size: int = 65536,
) -> str:
    """Calculate the hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        chunk_size: Number of bytes to read at a time

    Returns:
        The hexadecimal digest of the file's hash
    """
    file_path = Path(file_path)
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def create_temp_file(
    suffix: str = None,
    prefix: str = None,
    dir: Union[str, Path] = None,
    text: bool = False,
) -> Path:
    """Create a temporary file and return its path.

    Args:
        suffix: File suffix (e.g., '.txt')
        prefix: File prefix
        dir: Directory to create the file in
        text: Whether to open in text mode

    Returns:
        Path to the created temporary file
    """
    # Ensure the directory exists
    if dir is not None:
        os.makedirs(dir, exist_ok=True)

    # Create the file
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
    os.close(fd)  # Close the file descriptor as we'll open it again later
    return Path(path)


def create_temp_dir(prefix: str = None, dir: Union[str, Path] = None) -> str:
    """Create a temporary directory and return its path.

    Args:
        prefix: Directory name prefix
        dir: Parent directory to create the temp dir in

    Returns:
        Path to the created temporary directory
    """
    return tempfile.mkdtemp(prefix=prefix, dir=dir)


def safe_remove(path: Union[str, Path]) -> bool:
    """Safely remove a file or directory.

    Args:
        path: Path to the file or directory to remove

    Returns:
        True if the file/directory was removed, False otherwise
    """
    try:
        path = Path(path)
        if path.is_file() or path.is_symlink():
            os.unlink(path)
        elif path.is_dir():
            shutil.rmtree(path)
        return True
    except (OSError, shutil.Error):
        return False


def ensure_directory(directory: Union[str, Path], mode: int = 0o755) -> Path:
    """Ensure that a directory exists.

    Args:
        directory: Path to the directory
        mode: Permissions to set on the directory (default: 0o755)

    Returns:
        Path to the directory
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=mode)
    return directory


def copy_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    overwrite: bool = False,
) -> bool:
    """Copy a file from src to dst.

    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Whether to overwrite an existing file

    Returns:
        True if the file was copied successfully, False otherwise
    """
    src = Path(src)
    dst = Path(dst)

    if not src.is_file():
        return False

    if dst.exists() and not overwrite:
        return False

    try:
        shutil.copy2(src, dst)
        return True
    except (IOError, OSError, shutil.Error):
        return False


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Get detailed information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary containing file information
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return {"exists": False, "path": str(file_path)}

    stat = file_path.stat()
    mime_type, encoding = get_mime_type(file_path)

    return {
        "exists": True,
        "path": str(file_path.absolute()),
        "name": file_path.name,
        "stem": file_path.stem,
        "suffix": file_path.suffix,
        "suffixes": file_path.suffixes,
        "parent": str(file_path.parent),
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "is_symlink": file_path.is_symlink(),
        "size": stat.st_size,
        "size_human": _format_size(stat.st_size),
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "accessed": stat.st_atime,
        "mode": oct(stat.st_mode)[-3:],
        "mime_type": mime_type,
        "encoding": encoding,
        "is_binary": is_binary_file(file_path) if file_path.is_file() else None,
    }


def _format_size(size: int, decimals: int = 2) -> str:
    """Format a size in bytes to a human-readable string.
    
    Args:
        size: Size in bytes
        decimals: Number of decimal places
        
    Returns:
        Formatted size string with unit
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        if unit != 'TB':  # Don't divide beyond TB
            size /= 1024.0
    return f"{size:.{decimals}f} {unit}"


def find_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = True,
    case_sensitive: bool = False,
) -> List[Path]:
    """Find files matching a pattern in a directory.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        recursive: Whether to search recursively
        case_sensitive: Whether search should be case-sensitive

    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []

    if case_sensitive:
        # Simple glob with case sensitivity
        if recursive:
            return list(directory.rglob(pattern))
        return list(directory.glob(pattern))
    else:
        # Case-insensitive search
        pattern = pattern.lower()
        matches = []

        def _match(p: Path) -> bool:
            return p.name.lower().endswith(pattern.lstrip("*"))

        if recursive:
            for p in directory.rglob("*"):
                if p.is_file() and _match(p):
                    matches.append(p)
        else:
            for p in directory.glob("*"):
                if p.is_file() and _match(p):
                    matches.append(p)

        return matches


def sanitize_filename(filename: str, replace_with: str = "_") -> str:
    """Sanitize a string to be used as a filename.

    Args:
        filename: The input string
        replace_with: Character to replace invalid characters with

    Returns:
        Sanitized filename
    """

    # Normalize unicode characters
    normalized = unicodedata.normalize('NFKD', str(filename))
    ascii_str = normalized.encode('ascii', 'ignore').decode('ascii')

    # Replace invalid characters and whitespace
    no_special = re.sub(r'[^\w\s-]', replace_with, ascii_str)
    no_whitespace = re.sub(r'[\s]+', replace_with, no_special)
    stripped = no_whitespace.strip(replace_with)

    # Handle empty result
    if not stripped:
        return f"unnamed{replace_with}file"

    # Limit length to 255 chars, preserving extension
    max_len = 255
    if len(stripped) > max_len:
        name, ext = os.path.splitext(stripped)
        ext = ext[:max(0, max_len - len(name) - 1)]
        stripped = name[:max(0, max_len - len(ext) - 1)] + ext

    return stripped
