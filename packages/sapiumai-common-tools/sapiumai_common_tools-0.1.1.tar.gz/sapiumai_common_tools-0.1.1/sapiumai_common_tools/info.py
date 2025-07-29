"""
info.py

This module exposes the project information from the pyproject.toml file.

Usage:

    from util.info import PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION
"""

import tomllib

from sapiumai_common_tools.logger import setup_logger

logger = setup_logger(name=__name__)
try:
    with open(file="pyproject.toml", mode="rb") as f:
        data = tomllib.load(f)

    # Project information
    PROJECT_NAME: str = data.get("project", {}).get("name", "")
    PROJECT_VERSION: str = data.get("project", {}).get("version", "")
    PROJECT_DESCRIPTION: str = data.get("project", {}).get("description", "")
    if not all([PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION]):
        logger.warning(
            msg="Project information not found in pyproject.toml."
            "Using defaults."
        )
        PROJECT_NAME = "Unknown"
        PROJECT_VERSION = "Unknown"
        PROJECT_DESCRIPTION = "Unknown"
except FileNotFoundError:
    logger.warning(
        msg="pyproject.toml not found. Using defaults for project"
        " information."
    )
    PROJECT_NAME = "Unknown"
    PROJECT_VERSION = "Unknown"
    PROJECT_DESCRIPTION = "Unknown"
