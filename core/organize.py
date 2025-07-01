"""
Organize module for SnapTidy.
Organizes files by date extracted from metadata.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from . import utils


logger = logging.getLogger(__name__)


def run(
    path: str,
    date_format: str = "year",
    dry_run: bool = False,
    logging_mode: bool = False,
    unclassified_folder: str = None,
) -> None:
    """
    Organize files by date extracted from metadata.

    Args:
        path: Directory path to process
        date_format: Format for date-based folder organization ("year" or "yearmonth")
        dry_run: If True, only show what would be done without making changes
        logging_mode: If True, log all operations to CSV
        unclassified_folder: Folder to move unclassified files to
    """
    # For now, just call the original implementation
    import sys

    sys.path.insert(0, "snaptidy")
    from snaptidy.organize import run as original_run

    original_run(
        path=path,
        date_format=date_format,
        dry_run=dry_run,
        logging_mode=logging_mode,
        unclassified_folder=unclassified_folder,
    )
