"""
Generic schema importer with dynamic module loading.

This module provides a generic interface for importing schemas from various formats
by dynamically loading specific importer modules.
"""

import importlib
from pathlib import Path
from typing import Any


def import_schema(importer_type: str, *args, **kwargs) -> Any:
    """
    Import schema using the specified importer module.

    Dynamically loads the importer module and calls its retrieve function.

    Args:
        importer_type: Name of the importer module (e.g., 'a5sql_mk2')
        *args, **kwargs: Arguments to pass to the retrieve function

    Returns:
        SchemaManager: The imported schema manager object

    Raises:
        ImportError: If the importer module cannot be found
        AttributeError: If the importer module doesn't have a retrieve function
    """
    try:
        # Dynamically import the importer module
        module = importlib.import_module(f'dbgear.importers.{importer_type}')

        # Get and execute the retrieve function
        if hasattr(module, 'retrieve'):
            return module.retrieve(*args, **kwargs)
        else:
            raise AttributeError(f"Module '{importer_type}' does not have 'retrieve' function")

    except ImportError as e:
        raise ImportError(f"Importer '{importer_type}' not found: {e}")


def list_importers() -> list[str]:
    """
    Get a list of available importer modules.

    Returns:
        List of available importer module names
    """
    importers_dir = Path(__file__).parent.parent / 'importers'
    if not importers_dir.exists():
        return []

    return [f.stem for f in importers_dir.glob('*.py') if f.stem != '__init__']
