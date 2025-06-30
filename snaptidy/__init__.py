"""
SnapTidy - A CLI tool for organizing files and removing duplicates.
"""

__version__ = "0.1.0"
__author__ = "Yongsok Kwon"
__email__ = "saisiot.dev@gmail.com"

from . import cli, flatten, dedup, organize, utils

__all__ = ["cli", "flatten", "dedup", "organize", "utils"]
