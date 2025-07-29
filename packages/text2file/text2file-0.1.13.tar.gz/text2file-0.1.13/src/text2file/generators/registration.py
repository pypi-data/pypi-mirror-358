"""Module for registering file generators."""

import sys
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, List, Optional, Set, TypeVar, cast

# Type variable for generator functions
GeneratorFunc = TypeVar("GeneratorFunc", bound=Callable[..., Path])


class GeneratorRegistry:
    """Singleton class to manage generator registration."""

    _instance: ClassVar[Optional["GeneratorRegistry"]] = None
    _generators: Dict[str, GeneratorFunc]
    _supported_extensions: Set[str]

    def __new__(cls) -> "GeneratorRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._generators = {}
            cls._instance._supported_extensions = set()
        return cls._instance

    def register_generator(self, ext: str, func: GeneratorFunc) -> None:
        """Register a generator function for a file extension."""
        ext = ext.lstrip(".").lower()
        self._generators[ext] = func
        self._supported_extensions.add(ext)
        print(f"DEBUG: Registered generator for .{ext}", file=sys.stderr)
        print(
            f"DEBUG: Current generators: {list(self._generators.keys())}",
            file=sys.stderr,
        )
        print(
            f"DEBUG: Current supported extensions: {self._supported_extensions}",
            file=sys.stderr,
        )

    def get_generator(self, ext: str) -> Optional[GeneratorFunc]:
        """Get the generator function for a file extension."""
        ext = ext.lstrip(".").lower()
        return self._generators.get(ext)

    def get_supported_extensions(self) -> Set[str]:
        """Get a set of all supported file extensions."""
        return self._supported_extensions.copy()


# Create a singleton instance of the registry
_registry = GeneratorRegistry()

# Public API functions
def register_generator(
    extensions: List[str],
) -> Callable[[GeneratorFunc], GeneratorFunc]:
    """Decorator to register a generator function for specific file extensions.

    This decorator can be used at module level to register a generator function.

    Args:
        extensions: List of file extensions (with or without leading dot) that this generator supports

    Returns:
        A decorator function that registers the generator
    """

    def decorator(func: GeneratorFunc) -> GeneratorFunc:
        """Register the generator function for the given extensions."""
        for ext in extensions:
            _registry.register_generator(ext, func)
        return func

    return decorator


def register_generator_directly(extensions: List[str], func: GeneratorFunc) -> None:
    """Directly register a generator function for specific file extensions.

    This function can be used to register a generator function without using the decorator syntax.

    Args:
        extensions: List of file extensions (with or without leading dot)
        func: The generator function to register
    """
    for ext in extensions:
        _registry.register_generator(ext, func)


def get_generator(extension: str) -> Optional[GeneratorFunc]:
    """Get the generator function for a file extension.

    Args:
        extension: File extension (with or without leading dot)

    Returns:
        Generator function if found, None otherwise
    """
    return _registry.get_generator(extension)


def get_supported_extensions() -> Set[str]:
    """Get a set of all supported file extensions.

    Returns:
        Set of supported file extensions (without leading dots)
    """
    return _registry.get_supported_extensions()
