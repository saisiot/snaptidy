"""
Organization module for SnapTidy.
Organizes files into folders based on their creation date.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from . import utils


logger = logging.getLogger(__name__)


def get_target_folder(file_path: str, date_format: str) -> str:
    """
    Determine the target folder based on file creation date.
    
    Args:
        file_path: Path to the file
        date_format: Format for date-based folder organization ('year' or 'yearmonth')
        
    Returns:
        Target folder name
    """
    date = utils.extract_date(file_path)
    
    if date_format == "year":
        return str(date.year)
    elif date_format == "yearmonth":
        return f"{date.year}{date.month:02d}"
    else:
        logger.warning(f"Unknown date format: {date_format}. Using 'year' as default.")
        return str(date.year)


def organize_files(directory: str, files: List[str], date_format: str, dry_run: bool) -> Tuple[Dict[str, int], int]:
    """
    Organize files into folders based on their creation date.
    
    Args:
        directory: Base directory
        files: List of file paths to organize
        date_format: Format for date-based folder organization ('year' or 'yearmonth')
        dry_run: If True, only show what would be done without making changes
        
    Returns:
        Tuple containing (dictionary of folder counts, total files organized)
    """
    folder_counts = {}
    total_organized = 0
    
    for file_path in files:
        try:
            # Get relative path to maintain directory structure
            rel_path = os.path.relpath(file_path, directory)
            
            # Skip files that are already in a date folder
            parent_dir = os.path.basename(os.path.dirname(file_path))
            if (date_format == "year" and parent_dir.isdigit() and len(parent_dir) == 4) or \
               (date_format == "yearmonth" and parent_dir.isdigit() and len(parent_dir) == 6):
                logger.debug(f"Skipping already organized file: {file_path}")
                continue
            
            # Determine target folder
            target_folder = get_target_folder(file_path, date_format)
            target_dir = os.path.join(directory, target_folder)
            target_path = os.path.join(target_dir, os.path.basename(file_path))
            
            # Create target directory if it doesn't exist
            if not os.path.exists(target_dir) and not dry_run:
                os.makedirs(target_dir)
            
            # Handle filename conflicts
            if os.path.exists(target_path) and not dry_run:
                base_name, ext = os.path.splitext(os.path.basename(file_path))
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            # Move the file
            logger.info(f"{'Would move' if dry_run else 'Moving'} {file_path} -> {target_path}")
            
            if not dry_run:
                shutil.move(file_path, target_path)
            
            # Update statistics
            folder_counts[target_folder] = folder_counts.get(target_folder, 0) + 1
            total_organized += 1
            
        except Exception as e:
            logger.error(f"Error organizing {file_path}: {str(e)}")
    
    return folder_counts, total_organized


def run(path: str, date_format: str = "year", dry_run: bool = False) -> None:
    """
    Organize files by date.
    
    Args:
        path: Target directory path
        date_format: Format for date-based folder organization ('year' or 'yearmonth')
        dry_run: If True, only show what would be done without making changes
    """
    path = os.path.abspath(path)
    logger.info(f"Organizing directory: {path}")
    logger.info(f"Date format: {date_format}, Dry run: {dry_run}")
    
    if not os.path.isdir(path):
        logger.error(f"'{path}' is not a directory.")
        return
    
    # Scan directory for files
    files_by_type = utils.scan_directory(path)
    
    # Combine image and video files (which have date metadata)
    media_files = files_by_type['images'] + files_by_type['videos']
    other_files = files_by_type['other']
    
    logger.info(f"Found {len(media_files)} media files and {len(other_files)} other files.")
    
    # Organize media files
    if media_files:
        logger.info(f"Organizing {len(media_files)} media files...")
        folder_counts, total_organized = organize_files(path, media_files, date_format, dry_run)
        
        # Log summary
        logger.info(f"{'Would organize' if dry_run else 'Organized'} {total_organized} files into {len(folder_counts)} folders:")
        for folder, count in sorted(folder_counts.items()):
            logger.info(f"  {folder}: {count} files")
    else:
        logger.info("No media files found to organize.")
    
    # Ask if user wants to organize other files too
    if other_files:
        logger.info(f"Found {len(other_files)} non-media files that can also be organized by file modification date.")
        logger.info("These will be organized based on file modification date instead of metadata.")
        
        # In a real CLI, we would prompt the user here.
        # For simplicity, let's organize them automatically
        logger.info(f"Organizing {len(other_files)} non-media files...")
        other_folder_counts, other_total_organized = organize_files(path, other_files, date_format, dry_run)
        
        # Log summary
        logger.info(f"{'Would organize' if dry_run else 'Organized'} {other_total_organized} non-media files.")
    
    logger.info("Organization completed.")