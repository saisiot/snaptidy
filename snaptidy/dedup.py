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


def find_similar_images(image_files: List[str], sensitivity: float, threads: int) -> List[DuplicateGroup]:
    """
    Find perceptually similar images.
    
    Args:
        image_files: List of image file paths
        sensitivity: Sensitivity threshold for similarity detection
        threads: Number of threads to use
        
    Returns:
        List of DuplicateGroup objects
    """
    logger.info(f"Finding similar images among {len(image_files)} files...")
    
    # Calculate perceptual hashes for all images in parallel
    def hash_image(file_path: str) -> Tuple[str, Tuple]:
        img_hash, width, height = utils.compute_image_hash(file_path)
        return file_path, (img_hash, width, height)
    
    image_hashes = utils.process_in_parallel(image_files, hash_image, threads)
    
    # Filter out failed hash calculations
    valid_image_hashes = [(path, data) for path, data in image_hashes if data[0] is not None]
    
    # Sort images by size (area) for prioritizing larger images
    valid_image_hashes.sort(key=lambda x: x[1][1] * x[1][2], reverse=True)
    
    duplicate_groups = []
    processed: Set[str] = set()
    
    # Compare each image with others
    for i, (file_path1, (hash1, _, _)) in enumerate(valid_image_hashes):
        if file_path1 in processed:
            continue
        
        # Create a new group with this image as original
        group = DuplicateGroup(file_path1)
        processed.add(file_path1)
        
        # Check for similar images
        for file_path2, (hash2, _, _) in valid_image_hashes[i+1:]:
            if file_path2 in processed:
                continue
                
            if utils.is_similar_image(hash1, hash2, sensitivity):
                group.add_duplicate(file_path2)
                processed.add(file_path2)
        
        # Only add groups with duplicates
        if group.duplicates:
            duplicate_groups.append(group)
    
    return duplicate_groups


def find_similar_videos(video_files: List[str], sensitivity: float, threads: int) -> List[DuplicateGroup]:
    """
    Find similar videos.
    
    Args:
        video_files: List of video file paths
        sensitivity: Sensitivity threshold for similarity detection
        threads: Number of threads to use
        
    Returns:
        List of DuplicateGroup objects
    """
    logger.info(f"Finding similar videos among {len(video_files)} files...")
    
    # Sort videos by size for prioritizing larger videos
    video_files.sort(key=utils.get_file_size, reverse=True)
    
    duplicate_groups = []
    processed: Set[str] = set()
    
    # Compare each video with others
    for i, file_path1 in enumerate(video_files):
        if file_path1 in processed:
            continue
        
        # Create a new group with this video as original
        group = DuplicateGroup(file_path1)
        processed.add(file_path1)
        
        # Check for similar videos (this is more expensive, so we parallelize the comparisons)
        def compare_video(file_path2: str) -> Tuple[str, bool]:
            if file_path2 in processed:
                return file_path2, False
            return file_path2, utils.compare_video_frames(file_path1, file_path2, sensitivity)
        
        # Only compare with videos not yet processed
        videos_to_compare = [v for v in video_files[i+1:] if v not in processed]
        
        # Limit the number of videos to compare to avoid excessive computation
        max_comparisons = min(len(videos_to_compare), 50)  # Arbitrary limit
        videos_to_compare = videos_to_compare[:max_comparisons]
        
        if videos_to_compare:
            comparison_results = utils.process_in_parallel(videos_to_compare, compare_video, threads)
            
            for file_path2, is_similar in comparison_results:
                if is_similar:
                    group.add_duplicate(file_path2)
                    processed.add(file_path2)
        
        # Only add groups with duplicates
        if group.duplicates:
            duplicate_groups.append(group)
    
    return duplicate_groups


def remove_duplicates(duplicate_groups: List[DuplicateGroup], dry_run: bool = False) -> Tuple[int, int]:
    """
    Remove duplicate files.
    
    Args:
        duplicate_groups: List of DuplicateGroup objects
        dry_run: If True, only show what would be done without making changes
        
    Returns:
        Tuple of (number of files removed, bytes recovered)
    """
    total_files_removed = 0
    total_bytes_recovered = 0
    
    for group in duplicate_groups:
        for duplicate in group.duplicates:
            # Log what would be done
            logger.info(f"{'Would remove' if dry_run else 'Removing'} duplicate: {duplicate}")
            logger.info(f"  Original: {group.original_file}")
            
            # Remove file if not in dry_run mode
            if not dry_run:
                try:
                    file_size = os.path.getsize(duplicate)
                    os.remove(duplicate)
                    total_files_removed += 1
                    total_bytes_recovered += file_size
                except Exception as e:
                    logger.error(f"Error removing {duplicate}: {str(e)}")
            else:
                total_files_removed += 1
                total_bytes_recovered += utils.get_file_size(duplicate)
    
    return total_files_removed, total_bytes_recovered


def run(path: str, sensitivity: float = 0.9, dry_run: bool = False, threads: int = None) -> None:
    """
    Run the deduplication process.
    
    Args:
        path: Target directory path
        sensitivity: Sensitivity threshold for perceptual similarity detection
        dry_run: If True, only show what would be done without making changes
        threads: Number of threads to use for parallel processing
    """
    path = os.path.abspath(path)
    logger.info(f"Deduplicating directory: {path}")
    logger.info(f"Sensitivity: {sensitivity}, Dry run: {dry_run}, Threads: {threads}")
    
    if not os.path.isdir(path):
        logger.error(f"'{path}' is not a directory.")
        return
    
    # Scan directory for files
    files_by_type = utils.scan_directory(path)
    
    total_files = sum(len(files) for files in files_by_type.values())
    logger.info(f"Found {total_files} files in total.")
    logger.info(f"  Images: {len(files_by_type['images'])}")
    logger.info(f"  Videos: {len(files_by_type['videos'])}")
    logger.info(f"  Other: {len(files_by_type['other'])}")
    
    all_duplicate_groups = []
    
    # Step 1: Find exact duplicates across all files
    all_files = sum(files_by_type.values(), [])
    exact_duplicate_groups = find_exact_duplicates(all_files, threads)
    
    logger.info(f"Found {len(exact_duplicate_groups)} groups of exact duplicates.")
    all_duplicate_groups.extend(exact_duplicate_groups.values())
    
    # Remove exact duplicates from further consideration
    processed_files = set()
    for group in exact_duplicate_groups.values():
        processed_files.update(group.get_all_files())
    
    # Filter out already processed files
    unprocessed_images = [f for f in files_by_type['images'] if f not in processed_files]
    unprocessed_videos = [f for f in files_by_type['videos'] if f not in processed_files]
    
    # Step 2: Find similar images based on perceptual hash
    if unprocessed_images:
        similar_image_groups = find_similar_images(unprocessed_images, sensitivity, threads)
        logger.info(f"Found {len(similar_image_groups)} groups of similar images.")
        all_duplicate_groups.extend(similar_image_groups)
        
        # Update processed files
        for group in similar_image_groups:
            processed_files.update(group.get_all_files())
    
    # Step 3: Find similar videos (more expensive operation)
    if unprocessed_videos:
        similar_video_groups = find_similar_videos(unprocessed_videos, sensitivity, threads)
        logger.info(f"Found {len(similar_video_groups)} groups of similar videos.")
        all_duplicate_groups.extend(similar_video_groups)
    
    # Step 4: Remove all duplicates
    if all_duplicate_groups:
        files_removed, bytes_recovered = remove_duplicates(all_duplicate_groups, dry_run)
        
        # Format byte size for human readability
        if bytes_recovered < 1024:
            size_str = f"{bytes_recovered} bytes"
        elif bytes_recovered < 1024 * 1024:
            size_str = f"{bytes_recovered / 1024:.2f} KB"
        elif bytes_recovered < 1024 * 1024 * 1024:
            size_str = f"{bytes_recovered / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{bytes_recovered / (1024 * 1024 * 1024):.2f} GB"
        
        action = "Would remove" if dry_run else "Removed"
        logger.info(f"{action} {files_removed} duplicate files, recovering {size_str}.")
    else:
        logger.info("No duplicates found.")
    
    logger.info("Deduplication completed.")