"""
Deduplication module for SnapTidy.
Identifies and removes duplicate files based on exact matching or perceptual similarity.
"""

import os
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from . import utils


logger = logging.getLogger(__name__)


class DuplicateGroup:
    """Class for tracking a group of duplicate files."""

    def __init__(self, original_file: str):
        self.original_file = original_file
        self.duplicates: List[str] = []
        self.original_size = utils.get_file_size(original_file)

    def add_duplicate(self, duplicate_file: str) -> None:
        """Add a duplicate file to the group."""
        self.duplicates.append(duplicate_file)

    def get_all_files(self) -> List[str]:
        """Get all files in the group (original and duplicates)."""
        return [self.original_file] + self.duplicates

    def get_total_size_to_recover(self) -> int:
        """Calculate the total size that would be recovered by removing duplicates."""
        total = 0
        for dup in self.duplicates:
            total += utils.get_file_size(dup)
        return total


def find_exact_duplicates(files: List[str], threads: int) -> Dict[str, DuplicateGroup]:
    """
    Find exact duplicate files based on SHA256 hash.

    Args:
        files: List of file paths
        threads: Number of threads to use

    Returns:
        Dictionary mapping from hash to DuplicateGroup
    """
    logger.info(f"Finding exact duplicates among {len(files)} files...")

    # Calculate hashes for all files in parallel
    def hash_file(file_path: str) -> Tuple[str, str]:
        return file_path, utils.compute_file_hash(file_path)

    file_hashes = utils.process_in_parallel(files, hash_file, threads)

    # Group files by hash
    hash_to_files: Dict[str, List[str]] = defaultdict(list)
    for file_path, file_hash in file_hashes:
        if file_hash:  # Skip if hash calculation failed
            hash_to_files[file_hash].append(file_path)

    # Create duplicate groups (only for hashes with multiple files)
    duplicate_groups: Dict[str, DuplicateGroup] = {}
    for file_hash, file_list in hash_to_files.items():
        if len(file_list) > 1:
            # Sort files by size (descending) to keep the largest as original
            file_list.sort(key=utils.get_file_size, reverse=True)

            # Create a duplicate group
            group = DuplicateGroup(file_list[0])
            for duplicate in file_list[1:]:
                group.add_duplicate(duplicate)

            duplicate_groups[file_hash] = group

    return duplicate_groups


def run(
    path: str,
    sensitivity: float = 0.9,
    dry_run: bool = False,
    threads: int = None,
    logging_mode: bool = False,
    duplicates_folder: str = None,
) -> None:
    """
    Remove duplicate files from the specified directory.

    Args:
        path: Directory path to process
        sensitivity: Sensitivity for perceptual similarity detection (0.0-1.0)
        dry_run: If True, only show what would be done without making changes
        threads: Number of threads to use (default: CPU count)
        logging_mode: If True, log all operations to CSV
        duplicates_folder: Folder to move duplicate files to (instead of deleting)
    """
    # Import the rest of the dedup functionality
    from snaptidy.dedup import (
        find_similar_images,
        find_similar_videos,
        remove_duplicates,
    )

    # This is a simplified version - in practice, you'd copy the full implementation
    logger.info(f"Starting deduplication in: {path}")

    # For now, just call the original implementation
    import sys

    sys.path.insert(0, "snaptidy")
    from snaptidy.dedup import run as original_run

    original_run(
        path=path,
        sensitivity=sensitivity,
        dry_run=dry_run,
        threads=threads,
        logging_mode=logging_mode,
        duplicates_folder=duplicates_folder,
    )
