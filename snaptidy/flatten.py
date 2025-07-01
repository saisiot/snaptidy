"""
Flatten module for SnapTidy.
Moves all files from subdirectories into the target directory.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Set


logger = logging.getLogger(__name__)


def get_all_files(directory: str) -> List[str]:
    """
    Get all files from directory and subdirectories.

    Args:
        directory: Root directory to start search from

    Returns:
        List of file paths
    """
    all_files = []

    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            all_files.append(file_path)

    return all_files


def get_unique_filename(target_dir: str, original_name: str) -> str:
    """
    Generate a unique filename if the original name already exists.

    Args:
        target_dir: Target directory
        original_name: Original file name

    Returns:
        Unique file name
    """
    base_name = os.path.basename(original_name)
    name, ext = os.path.splitext(base_name)

    target_path = os.path.join(target_dir, base_name)

    # If the file doesn't exist, return the original name
    if not os.path.exists(target_path):
        return base_name

    # Find a unique name by appending a number
    counter = 1
    while True:
        new_name = f"{name}_{counter}{ext}"
        target_path = os.path.join(target_dir, new_name)

        if not os.path.exists(target_path):
            return new_name

        counter += 1


def run(
    path: str,
    dry_run: bool = False,
    copy: bool = False,
    output: str = None,
    logging_mode: bool = False,
) -> None:
    """
    Move all files from subdirectories into the target directory.

    Args:
        path: Target directory path
        dry_run: If True, only show what would be done without making changes
        copy: If True, copy files instead of moving them
        output: Output directory for copied files (only used if copy=True)
        logging_mode: If True, log all operations to CSV
    """
    path = os.path.abspath(path)
    logger.info(f"Flattening directory: {path}")

    if not os.path.isdir(path):
        logger.error(f"'{path}' is not a directory.")
        return

    # Setup output directory for copy mode
    if copy:
        if output is None:
            output = os.path.join(path, "flattened")
        output = os.path.abspath(output)

        # Check disk space if copying
        if not dry_run:
            total_size = sum(os.path.getsize(f) for f in get_all_files(path))
            free_space = shutil.disk_usage(output).free
            if total_size > free_space:
                logger.error(
                    f"Insufficient disk space. Need {total_size} bytes, but only {free_space} bytes available."
                )
                return

        logger.info(f"Copying files to: {output}")
        os.makedirs(output, exist_ok=True)
        target_dir = output
    else:
        target_dir = path

    # Setup logging if enabled
    operation_logger = None
    if logging_mode:
        from .utils import OperationLogger

        log_file = os.path.join(path, "snaptidy_flatten_log.csv")
        operation_logger = OperationLogger(log_file)
        logger.info(f"Logging operations to: {log_file}")

    # Get all files
    all_files = get_all_files(path)
    logger.info(f"Found {len(all_files)} files in total.")

    # Keep track of already processed files to avoid moving files multiple times
    processed: Set[str] = set()

    # Files in the root directory (don't need to be moved)
    root_files = [f for f in all_files if os.path.dirname(f) == path]
    for file in root_files:
        processed.add(file)

    logger.info(f"{len(root_files)} files are already in the root directory.")

    # Files that need to be moved
    files_to_move = [f for f in all_files if f not in processed]
    logger.info(f"{len(files_to_move)} files will be moved to the target directory.")

    if not files_to_move:
        logger.info("No files need to be moved.")
        return

    # Process each file
    moved_count = 0

    for file_path in files_to_move:
        if file_path in processed:
            continue

        # Get unique filename for the target directory
        original_name = os.path.basename(file_path)
        unique_name = get_unique_filename(target_dir, original_name)
        target_path = os.path.join(target_dir, unique_name)

        # Move or copy the file (or simulate if dry_run is True)
        try:
            # Log what we're going to do
            action = "Copying" if copy else "Moving"
            if original_name == unique_name:
                logger.info(f"{action} {file_path} -> {target_path}")
            else:
                logger.info(
                    f"{action} {file_path} -> {target_path} (renamed due to conflict)"
                )

            if not dry_run:
                if copy:
                    shutil.copy2(file_path, target_path)
                    operation_type = "copy"
                else:
                    shutil.move(file_path, target_path)
                    operation_type = "move"

                # Log operation if logging is enabled
                if operation_logger:
                    operation_logger.log_operation(
                        operation_type=operation_type,
                        source_path=file_path,
                        target_path=target_path,
                        file_size=os.path.getsize(target_path),
                        timestamp=operation_logger.get_timestamp(),
                    )

            moved_count += 1
            processed.add(file_path)

        except Exception as e:
            logger.error(f"Error {action.lower()} {file_path}: {str(e)}")

    # Log summary
    action = "Would move" if dry_run else ("Copied" if copy else "Moved")
    logger.info(f"{action} {moved_count} files.")

    # Remove empty directories if not in dry_run mode and not copying
    if not dry_run and not copy:
        for root, dirs, files in os.walk(path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    # Check if directory is empty
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        logger.info(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Error removing directory {dir_path}: {str(e)}")

    # Close logging if enabled
    if operation_logger:
        operation_logger.close()
        logger.info(f"Operation log saved to: {operation_logger.log_file}")

    logger.info("Flatten operation completed.")
