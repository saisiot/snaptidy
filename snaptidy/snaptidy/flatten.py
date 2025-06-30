"""
Flatten module for SnapTidy.
Moves all files from subdirectories into the target directory.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Set, Optional
from . import utils


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
    path: str, dry_run: bool = False, copy: bool = False, output: Optional[str] = None
) -> None:
    """
    Move or copy all files from subdirectories into the target directory or output directory.
    Args:
        path: Target directory path
        dry_run: If True, only show what would be done without making changes
        copy: If True, copy files instead of moving
        output: Output directory for flattened files (used only if copy is True)
    """
    path = os.path.abspath(path)
    if copy:
        if output is None:
            output = os.path.join(path, "flattened")
        output = os.path.abspath(output)
        if not os.path.exists(output) and not dry_run:
            os.makedirs(output)
    else:
        output = path
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

    # 용량 체크 (copy 모드만)
    if copy:
        total_size = sum(os.path.getsize(f) for f in files_to_process)
        free_space = utils.get_disk_free_space(output)
        logger.info(
            f"Total size to copy: {total_size} bytes, Free space: {free_space} bytes"
        )
        if total_size > free_space:
            logger.error("Not enough disk space to copy all files. Operation aborted.")
            return

    processed_count = 0
    for file_path in files_to_process:
        original_name = os.path.basename(file_path)
        unique_name = get_unique_filename(output, original_name)
        target_path = os.path.join(output, unique_name)
        try:
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
