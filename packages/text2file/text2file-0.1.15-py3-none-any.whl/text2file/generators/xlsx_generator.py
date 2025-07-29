"""Generator for Excel (.xlsx) files."""

from pathlib import Path
from typing import Any

import openpyxl

from .base import BaseGenerator


class XLSXGenerator(BaseGenerator):
    """Generator for Excel (.xlsx) files."""

    EXTENSIONS = {"xlsx"}

    @classmethod
    def generate(
        cls,
        content: str,
        output_path: Path,
        **kwargs: Any,
    ) -> Path:
        """
        Generate an Excel file from the given content.

        Args:
            content: The content to write to the file. For XLSX, this should be
                a CSV-like string where rows are separated by newlines and
                cells by commas.
            output_path: The path where the file should be saved.
            **kwargs: Additional options for file generation.
                - sheet_name: Name of the worksheet (default: 'Sheet1')
                - auto_adjust: Whether to auto-adjust column widths (default: True)
        """
        # Create a new workbook and select the active worksheet
        workbook = openpyxl.Workbook()
        try:
            sheet_name = kwargs.get("sheet_name", "Sheet1")
            worksheet = workbook.active
            worksheet.title = sheet_name

            # Parse the CSV-like content
            rows = [line.split(",") for line in content.strip().split("\n")]
            # Write data to the worksheet
            for row_idx, row in enumerate(rows, 1):
                for col_idx, value in enumerate(row, 1):
                    worksheet.cell(row=row_idx, column=col_idx, value=value.strip())

            # Auto-adjust column widths if requested
            if kwargs.get("auto_adjust", True):
                for column_cells in worksheet.columns:
                    if not column_cells:  # Skip empty columns
                        continue
                    max_length = 0
                    # Get the column name
                    column = column_cells[0].column_letter
                    for cell in column_cells:
                        try:
                            if cell.value and len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except Exception:  # noqa: BLE001
                            continue
                    if max_length > 0:
                        adjusted_width = (max_length + 2) * 1.2
                        worksheet.column_dimensions[column].width = adjusted_width

            # Save the workbook
            workbook.save(output_path)
            return output_path

        except Exception as e:
            raise IOError(f"Failed to save XLSX file: {e}") from e
        finally:
            try:
                workbook.close()
            except Exception:  # noqa: BLE001
                pass  # Ignore errors during cleanup

    @classmethod
    def cleanup(cls) -> None:
        """Clean up any resources used by the generator."""
        # No cleanup needed as we're using context managers in generate()
        pass


def register(registry):
    """Register the XLSX generator."""
    registry.register(XLSXGenerator())
