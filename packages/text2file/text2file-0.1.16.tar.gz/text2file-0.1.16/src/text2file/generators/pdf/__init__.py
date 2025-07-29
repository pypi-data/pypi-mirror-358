"""PDF file generators."""

from pathlib import Path
from typing import Any, Optional, Tuple, Type

from ...generators.registration import register_generator_directly


def _get_fpdf() -> Tuple[Optional[Type], Optional[Type], Optional[Type]]:
    """Lazy import of fpdf2 to make it an optional dependency."""
    try:
        from fpdf import FPDF, XPos, YPos

        return FPDF, XPos, YPos
    except ImportError:
        return None, None, None


def generate_pdf_file(content: str, output_path: Path, **kwargs: Any) -> Path:
    """Generate a PDF file with the given content.

    Args:
        content: Text content to include in the PDF
        output_path: Path where the PDF should be saved
        **kwargs: Additional keyword arguments (ignored)

    Returns:
        Path to the generated PDF file

    Raises:
        ImportError: If fpdf2 is not installed
    """
    FPDF, XPos, YPos = _get_fpdf()
    if FPDF is None or XPos is None or YPos is None:
        raise ImportError(
            "fpdf2 is required for PDF generation. Install with: pip install fpdf2"
        )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Set margins (1 inch = 25.4 mm)
    margin = 25.4
    pdf.set_margins(margin, margin, margin)

    # Calculate available width
    available_width = pdf.w - 2 * margin

    # Split content into paragraphs
    paragraphs = content.split("\n\n")

    for para in paragraphs:
        if not para.strip():
            pdf.ln(10)  # Add space between paragraphs
            continue

        # Split into lines that fit the page width
        lines = pdf.multi_cell(
            w=available_width, h=10, txt=para, split_only=True  # line height
        )

        # Add each line to the PDF
        for line in lines:
            pdf.cell(
                w=available_width,
                h=10,  # line height
                txt=line,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

        # Add space after paragraph
        pdf.ln(5)

    # Save the PDF
    pdf.output(str(output_path))
    return output_path


# Register the PDF generator
register_generator_directly(["pdf"], generate_pdf_file)
