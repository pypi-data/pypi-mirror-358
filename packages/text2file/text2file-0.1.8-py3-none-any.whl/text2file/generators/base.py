"""Base class for file generators."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union


class BaseGenerator(ABC):
    """Abstract base class for all file generators."""

    @classmethod
    @abstractmethod
    def generate(
        cls,
        content: str,
        output_path: Union[str, Path],
        **kwargs: Any,
    ) -> Path:
        """Generate a file with the given content.

        Args:
            content: The content to write to the file
            output_path: Path where the file should be created
            **kwargs: Additional generator-specific arguments

        Returns:
            Path to the generated file
        """
        raise NotImplementedError("Subclasses must implement generate()")
