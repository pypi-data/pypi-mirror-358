"""
Utility functions for AD User Manager.
"""

import tomllib
from pathlib import Path


def get_version() -> str:
    """
    Read version from pyproject.toml.

    Returns:
        Version string from pyproject.toml

    Raises:
        FileNotFoundError: If pyproject.toml is not found
        KeyError: If version is not found in pyproject.toml
    """
    try:
        # Get path to pyproject.toml (one level up from package directory)
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        return data["project"]["version"]

    except FileNotFoundError:
        # Fallback version if pyproject.toml is not found
        return "0.1.0"
    except KeyError:
        # Fallback version if version key is not found
        return "0.1.0"
