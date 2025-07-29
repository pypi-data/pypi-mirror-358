"""Validators for text-based file formats."""

import csv
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict

import yaml

from .base import BaseValidator, ValidationResult


class TextFileValidator(BaseValidator):
    """Validator for plain text files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for non-printable characters (excluding standard whitespace)
            for i, char in enumerate(content):
                if ord(char) < 32 and char not in "\n\r\t":
                    return ValidationResult(
                        is_valid=False,
                        message=f"File contains non-printable character at position {i}",
                        details={"position": i, "character": repr(char)},
                    )

            return ValidationResult(is_valid=True, message="File is a valid text file")

        except UnicodeDecodeError:
            return ValidationResult(
                is_valid=False, message="File is not valid UTF-8 text"
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating text file: {str(e)}",
                details={"error": str(e)},
            )


class JsonFileValidator(TextFileValidator):
    """Validator for JSON files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a JSON file."""
        # First validate as text
        text_result = super().validate(file_path)
        if not text_result.is_valid:
            return text_result

        # Then validate JSON syntax
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            return ValidationResult(is_valid=True, message="File is valid JSON")
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid JSON: {str(e)}",
                details={"error": str(e), "line": e.lineno, "column": e.colno},
            )


class CsvFileValidator(TextFileValidator):
    """Validator for CSV files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a CSV file."""
        # First validate as text
        text_result = super().validate(file_path)
        if not text_result.is_valid:
            return text_result

        # Then validate CSV format
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                # Try to read the CSV to check for syntax errors
                reader = csv.reader(f)
                rows = list(reader)

                if not rows:
                    return ValidationResult(
                        is_valid=True, message="File is a valid (empty) CSV"
                    )

                # Check that all rows have the same number of columns as the header
                num_columns = len(rows[0])
                for i, row in enumerate(rows[1:], 2):  # Start from row 2 (1-based)
                    if len(row) != num_columns:
                        return ValidationResult(
                            is_valid=False,
                            message=f"Row {i} has {len(row)} columns, expected {num_columns}",
                            details={
                                "row": i,
                                "found_columns": len(row),
                                "expected_columns": num_columns,
                            },
                        )

            return ValidationResult(
                is_valid=True,
                message=f"File is a valid CSV with {len(rows)} rows and {num_columns} columns",
            )

        except csv.Error as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid CSV: {str(e)}",
                details={"error": str(e)},
            )


class XmlFileValidator(TextFileValidator):
    """Validator for XML files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate an XML file."""
        # First validate as text
        text_result = super().validate(file_path)
        if not text_result.is_valid:
            return text_result

        # Then validate XML syntax
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ET.parse(f)
            return ValidationResult(is_valid=True, message="File is valid XML")
        except ET.ParseError as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid XML: {str(e)}",
                details={
                    "error": str(e),
                    "position": e.position if hasattr(e, "position") else None,
                },
            )


class YamlFileValidator(TextFileValidator):
    """Validator for YAML files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a YAML file."""
        # First validate as text
        text_result = super().validate(file_path)
        if not text_result.is_valid:
            return text_result

        # Then validate YAML syntax
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
            return ValidationResult(is_valid=True, message="File is valid YAML")
        except yaml.YAMLError as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid YAML: {str(e)}",
                details={"error": str(e)},
            )


class HtmlFileValidator(TextFileValidator):
    """Validator for HTML files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate an HTML file."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # If BeautifulSoup is not available, fall back to basic text validation
            return super().validate(file_path)

        # First validate as text
        text_result = super().validate(file_path)
        if not text_result.is_valid:
            return text_result

        # Then validate HTML syntax with BeautifulSoup
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

                # Check for parse errors
                if soup.find() is None:
                    return ValidationResult(
                        is_valid=False, message="No valid HTML content found"
                    )

                return ValidationResult(is_valid=True, message="File is valid HTML")

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error parsing HTML: {str(e)}",
                details={"error": str(e)},
            )


class CssFileValidator(TextFileValidator):
    """Validator for CSS files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a CSS file."""
        # For now, just do basic text validation
        # In a real implementation, you might want to use a CSS parser
        return super().validate(file_path)


class JavaScriptFileValidator(TextFileValidator):
    """Validator for JavaScript files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a JavaScript file."""
        # For now, just do basic text validation
        # In a real implementation, you might want to use a JS parser
        return super().validate(file_path)


class PythonFileValidator(BaseValidator):
    """Validator for Python files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a Python file."""
        try:
            # First validate as a text file
            text_result = TextFileValidator.validate(file_path)
            if not text_result.is_valid:
                return text_result

            # Try to parse the Python file
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    # Use compile to check syntax without executing
                    compile(f.read(), file_path, "exec")
                except SyntaxError as e:
                    return ValidationResult(
                        is_valid=False,
                        message=f"Invalid Python syntax: {e.msg}",
                        details={
                            "line": e.lineno,
                            "column": e.offset or 0,
                            "message": e.msg,
                        },
                    )

            return ValidationResult(
                is_valid=True,
                message="Valid Python file",
                details={"lines": sum(1 for _ in open(file_path, "rb"))},
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating Python file: {str(e)}",
                details={"error": str(e)},
            )


class ShellScriptValidator(BaseValidator):
    """Validator for shell script files."""

    @classmethod
    def validate(cls, file_path: str) -> ValidationResult:
        """Validate a shell script file."""
        try:
            # First validate as a text file
            text_result = TextFileValidator.validate(file_path)
            if not text_result.is_valid:
                return text_result

            # Check if file is executable (if on Unix-like system)
            if hasattr(os, "access") and os.access(file_path, os.X_OK):
                return ValidationResult(
                    is_valid=True,
                    message="Valid shell script (executable)",
                    details={"executable": True},
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    message="Valid shell script (not executable)",
                    details={"executable": False},
                )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error validating shell script: {str(e)}",
                details={"error": str(e)},
            )
