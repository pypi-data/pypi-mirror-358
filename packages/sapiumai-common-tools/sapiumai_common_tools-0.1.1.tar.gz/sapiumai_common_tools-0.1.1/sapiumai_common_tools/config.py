"""
config.py

This module provides functionality to load the application configuration
from a JSON file located in the './config' directory. It defines:

- load_config: Reads 'config.json' and returns its contents as a NestedConfig.
- config: A module-level variable holding the loaded configuration.

If the configuration file is missing or cannot be read, an empty config
dictionary is returned and an error is logged.
"""

import json
from os import path
from typing import Union

from sapiumai_common_tools.logger import setup_logger

logger = setup_logger(name=__name__)


Primitive = Union[str, int, float, bool]
NestedConfig = dict[str, dict[str, Primitive]]


def load_config() -> NestedConfig:
    """
    Loads the config file.

    Returns:
        NestedConfig: The config file as a nested dictionary.
    """
    CONFIG_PATH = "./config"
    try:
        filename = path.join(CONFIG_PATH, "config.json")
        with open(file=filename, mode="r") as f:
            return json.load(fp=f)
    except FileNotFoundError as e:
        logger.error(msg=f"Error loading config: {e}")
        return {}


config: NestedConfig = load_config()
