"""Validators for different file formats."""

from .archive_validator import (
    ArchiveValidator,
    Bzip2Validator,
    GzipValidator,
    TarBz2Validator,
    TarGzValidator,
    TarValidator,
    ZipValidator,
)
from .base import BaseValidator, ValidationResult, get_validator
from .image_validator import (
    BmpValidator,
    GifValidator,
    ImageValidator,
    JpegValidator,
    PngValidator,
    SvgValidator,
    WebPValidator,
)
from .office_validator import (
    DocValidator,
    DocxValidator,
    OdpValidator,
    OdsValidator,
    OdtValidator,
    OfficeValidator,
    PptValidator,
    PptxValidator,
    XlsValidator,
    XlsxValidator,
)
from .pdf_validator import PdfValidator
from .text_validator import (
    CssFileValidator,
    CsvFileValidator,
    HtmlFileValidator,
    JavaScriptFileValidator,
    JsonFileValidator,
    PythonFileValidator,
    ShellScriptValidator,
    TextFileValidator,
    XmlFileValidator,
    YamlFileValidator,
)
from .video_validator import (  # Add other video validators as needed
    AviValidator,
    MkvValidator,
    MovValidator,
    Mp4Validator,
    VideoValidator,
    WebmValidator,
)

# Export all validators
__all__ = [
    # Base
    "BaseValidator",
    "ValidationResult",
    "get_validator",
    # Text
    "TextFileValidator",
    "JsonFileValidator",
    "CsvFileValidator",
    "XmlFileValidator",
    "YamlFileValidator",
    "HtmlFileValidator",
    "CssFileValidator",
    "JavaScriptFileValidator",
    "PythonFileValidator",
    "ShellScriptValidator",
    # Images
    "ImageValidator",
    "JpegValidator",
    "PngValidator",
    "GifValidator",
    "BmpValidator",
    "WebPValidator",
    "SvgValidator",
    # Archives
    "ArchiveValidator",
    "ZipValidator",
    "TarValidator",
    "TarGzValidator",
    "TarBz2Validator",
    "GzipValidator",
    "Bzip2Validator",
    # PDF
    "PdfValidator",
    # Office
    "OfficeValidator",
    "DocxValidator",
    "XlsxValidator",
    "PptxValidator",
    "OdtValidator",
    "OdsValidator",
    "OdpValidator",
    "DocValidator",
    "XlsValidator",
    "PptValidator",
    # Video
    "VideoValidator",
    "Mp4Validator",
    "AviValidator",
    "MovValidator",
    "MkvValidator",
    "WebmValidator",
    # Add other video validators to __all__ as needed
]
