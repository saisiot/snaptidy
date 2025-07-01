"""
Flatten module for SnapTidy.
Moves all files from subdirectories into the target directory.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Set, Optional, Tuple
from .utils import OperationLogger


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
    output: Optional[str] = None,
    logging_mode: bool = False,
) -> None:
    """
    Move or copy all files from subdirectories into the target directory or output directory.
    Args:
        path: Target directory path
        dry_run: If True, only show what would be done without making changes
        copy: If True, copy files instead of moving
        output: Output directory for flattened files (used only if copy is True)
        logging_mode: If True, log all operations for recovery
    """
    path = os.path.abspath(path)

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
                print(
                    f"Insufficient disk space. Need {total_size} bytes, but only {free_space} bytes available."
                )
                return
        print(f"Copying files to: {output}")
        os.makedirs(output, exist_ok=True)
        target_dir = output
    else:
        target_dir = path

    # Setup logging if enabled
    operation_logger = None
    if logging_mode:
        log_file = os.path.join(path, "snaptidy_flatten_log.csv")
        operation_logger = OperationLogger(log_file)
        print(f"Logging operations to: {log_file}")

    logger.info(f"Flattening directory: {path}{' (copy mode)' if copy else ''}")
    logger.info(f"Output directory: {output}")

    if not os.path.isdir(path):
        logger.error(f"'{path}' is not a directory.")
        return

    all_files = get_all_files(path)
    logger.info(f"Found {len(all_files)} files in total.")

    # Files in the root/output directory (don't need to be moved/copied)
    root_files = [f for f in all_files if os.path.dirname(f) == output]
    processed: Set[str] = set(root_files)
    logger.info(f"{len(root_files)} files are already in the output directory.")

    files_to_process = [f for f in all_files if f not in processed]
    logger.info(
        f"{len(files_to_process)} files will be {'copied' if copy else 'moved'} to the output directory."
    )

    if not files_to_process:
        logger.info(f"No files need to be {'copied' if copy else 'moved'}.")
        return

    processed_count = 0
    for file_path in files_to_process:
        original_name = os.path.basename(file_path)
        unique_name = get_unique_filename(output, original_name)
        target_path = os.path.join(output, unique_name)
        try:
            # Log the operation if logging is enabled
            if operation_logger:
                operation_type = "copy" if copy else "move"
                operation_logger.log_operation(
                    operation_type=operation_type,
                    source_path=file_path,
                    target_path=target_path,
                )

            if copy:
                logger.info(
                    f"{'Would copy' if dry_run else 'Copying'} {file_path} -> {target_path}"
                )
                if not dry_run:
                    shutil.copy2(file_path, target_path)
            else:
                logger.info(
                    f"{'Would move' if dry_run else 'Moving'} {file_path} -> {target_path}"
                )
                if not dry_run:
                    shutil.move(file_path, target_path)
            processed_count += 1
            processed.add(file_path)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")

    action = (
        "Would copy"
        if dry_run and copy
        else ("Would move" if dry_run else ("Copied" if copy else "Moved"))
    )
    logger.info(f"{action} {processed_count} files.")

    # Remove empty directories if not in dry_run mode and not copy mode
    if not dry_run and not copy:
        for root, dirs, files in os.walk(path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        logger.info(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Error removing directory {dir_path}: {str(e)}")
    logger.info("Flatten operation completed.")

    if operation_logger:
        print(f"Operation log saved to: {operation_logger.log_file}")


def flatten_directory(
    directory: str,
    files: List[str],
    copy_mode: bool = False,
    output_folder: str = None,
    dry_run: bool = False,
    logger_instance=None,
) -> Tuple[int, int]:
    """
    Flatten a directory by moving all files to the root level.

    Args:
        directory: Base directory
        files: List of file paths to flatten
        copy_mode: If True, copy files instead of moving them
        output_folder: If specified, move/copy files to this subfolder
        dry_run: If True, only show what would be done without making changes
        logger_instance: OperationLogger instance for tracking operations

    Returns:
        Tuple containing (number of files processed, total bytes processed)
    """
    total_files = 0
    total_bytes = 0

    for file_path in files:
        try:
            # Get relative path to maintain directory structure
            rel_path = os.path.relpath(file_path, directory)

            # Determine target path
            if output_folder:
                target_dir = os.path.join(directory, output_folder)
                target_path = os.path.join(target_dir, os.path.basename(file_path))
            else:
                target_path = os.path.join(directory, os.path.basename(file_path))

            # Create target directory if it doesn't exist
            if not os.path.exists(os.path.dirname(target_path)) and not dry_run:
                os.makedirs(os.path.dirname(target_path))

            # Handle filename conflicts
            if os.path.exists(target_path) and not dry_run:
                base_name, ext = os.path.splitext(os.path.basename(file_path))
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(os.path.dirname(target_path), new_name)
                    counter += 1

            # Log the operation
            if logger_instance:
                operation_type = "copy" if copy_mode else "move"
                logger_instance.log_operation(
                    operation_type=operation_type,
                    source_path=file_path,
                    target_path=target_path,
                )

            # Perform the operation
            if copy_mode:
                logger.info(
                    f"{'Would copy' if dry_run else 'Copying'} {file_path} -> {target_path}"
                )
                if not dry_run:
                    shutil.copy2(file_path, target_path)
            else:
                logger.info(
                    f"{'Would move' if dry_run else 'Moving'} {file_path} -> {target_path}"
                )
                if not dry_run:
                    shutil.move(file_path, target_path)

            # Update statistics
            file_size = os.path.getsize(file_path)
            total_files += 1
            total_bytes += file_size

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")

    return total_files, total_bytes
