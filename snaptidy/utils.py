"""
Utility functions for SnapTidy.
"""

import os
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import concurrent.futures

import exifread
from PIL import Image
import imagehash
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import cv2


logger = logging.getLogger(__name__)


def compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """
    Compute SHA256 hash of a file.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read
        
    Returns:
        SHA256 hash as a hexadecimal string
    """
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error computing hash for {file_path}: {str(e)}")
        return ""


def compute_image_hash(image_path: str) -> Tuple[Union[imagehash.ImageHash, None], int, int]:
    """
    Compute perceptual hash of an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple containing (ImageHash object, width, height)
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        img_hash = imagehash.phash(img)
        img.close()
        return img_hash, width, height
    except Exception as e:
        logger.error(f"Error computing image hash for {image_path}: {str(e)}")
        return None, 0, 0


def is_similar_image(img1_hash: imagehash.ImageHash, 
                     img2_hash: imagehash.ImageHash, 
                     sensitivity: float = 0.9) -> bool:
    """
    Check if two images are similar using their perceptual hashes.
    
    Args:
        img1_hash: Perceptual hash of first image
        img2_hash: Perceptual hash of second image
        sensitivity: Sensitivity threshold (0.0-1.0)
        
    Returns:
        True if images are similar, False otherwise
    """
    if img1_hash is None or img2_hash is None:
        return False
    
    # Convert sensitivity to hash difference threshold
    # Higher sensitivity = lower threshold
    max_hash_diff = 64  # Maximum possible hash difference (64-bit hash)
    threshold = int(max_hash_diff * (1 - sensitivity))
    
    # Calculate difference between hashes
    difference = img1_hash - img2_hash
    return difference <= threshold


def extract_date_from_exif(file_path: str) -> Optional[datetime]:
    """
    Extract date from EXIF data of an image.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        datetime object or None if extraction fails
    """
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            
        # Try different EXIF date tags
        date_tags = [
            'EXIF DateTimeOriginal',
            'EXIF DateTimeDigitized',
            'Image DateTime'
        ]
        
        for tag in date_tags:
            if tag in tags:
                date_str = str(tags[tag])
                # Common format: "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        
        # If no EXIF date found, use file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    
    except Exception as e:
        logger.debug(f"Error extracting EXIF date from {file_path}: {str(e)}")
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))


def extract_date_from_video(file_path: str) -> Optional[datetime]:
    """
    Extract date from video metadata.
    
    Args:
        file_path: Path to the video file
        
    Returns:
        datetime object or None if extraction fails
    """
    try:
        # Try using hachoir
        parser = createParser(file_path)
        if parser:
            metadata = extractMetadata(parser)
            if metadata and metadata.has("creation_date"):
                return metadata.get("creation_date")
        
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    
    except Exception as e:
        logger.debug(f"Error extracting date from video {file_path}: {str(e)}")
        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))


def extract_date(file_path: str) -> datetime:
    """
    Extract creation date from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        datetime object
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Image formats
    if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.heic']:
        date = extract_date_from_exif(file_path)
    
    # Video formats
    elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
        date = extract_date_from_video(file_path)
    
    # Default to file modification time for other formats
    else:
        date = datetime.fromtimestamp(os.path.getmtime(file_path))
    
    # If all extraction methods failed, use file modification date
    if date is None:
        date = datetime.fromtimestamp(os.path.getmtime(file_path))
    
    return date


def compare_video_frames(video1_path: str, video2_path: str, sensitivity: float = 0.9) -> bool:
    """
    Compare two videos by sampling frames and checking similarity.
    
    Args:
        video1_path: Path to first video
        video2_path: Path to second video
        sensitivity: Sensitivity threshold (0.0-1.0)
        
    Returns:
        True if videos are similar, False otherwise
    """
    try:
        # Open videos
        vid1 = cv2.VideoCapture(video1_path)
        vid2 = cv2.VideoCapture(video2_path)
        
        # Get video properties
        frame_count1 = int(vid1.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count2 = int(vid2.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # If frame counts differ significantly, videos are likely different
        if abs(frame_count1 - frame_count2) / max(frame_count1, frame_count2) > 0.2:
            return False
        
        # Sample frames (e.g., 10% of frames, up to 50)
        sample_count = min(50, max(5, int(min(frame_count1, frame_count2) * 0.1)))
        step = max(frame_count1, frame_count2) // sample_count
        
        similar_frames = 0
        
        for i in range(0, min(frame_count1, frame_count2), step):
            # Set position
            vid1.set(cv2.CAP_PROP_POS_FRAMES, min(i, frame_count1 - 1))
            vid2.set(cv2.CAP_PROP_POS_FRAMES, min(i, frame_count2 - 1))
            
            # Read frames
            ret1, frame1 = vid1.read()
            ret2, frame2 = vid2.read()
            
            if not ret1 or not ret2:
                continue
            
            # Convert to grayscale for better comparison
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Resize to same dimensions for comparison
            height = 200
            ratio = height / gray1.shape[0]
            width = int(gray1.shape[1] * ratio)
            dim = (width, height)
            gray1 = cv2.resize(gray1, dim)
            gray2 = cv2.resize(gray2, dim)
            
            # Compare using structural similarity
            score, _ = cv2.compareHist(
                cv2.calcHist([gray1], [0], None, [256], [0, 256]),
                cv2.calcHist([gray2], [0], None, [256], [0, 256]),
                cv2.HISTCMP_CORREL
            )
            
            if score > sensitivity:
                similar_frames += 1
        
        # Calculate similarity percentage
        similarity = similar_frames / sample_count
        
        # Videos are similar if enough frames are similar
        return similarity >= sensitivity
    
    except Exception as e:
        logger.error(f"Error comparing videos {video1_path} and {video2_path}: {str(e)}")
        return False
    finally:
        # Release video captures
        if 'vid1' in locals():
            vid1.release()
        if 'vid2' in locals():
            vid2.release()


def is_image_file(file_path: str) -> bool:
    """Check if file is an image based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic']


def is_video_file(file_path: str) -> bool:
    """Check if file is a video based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.m4v', '.3gp']


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def scan_directory(directory: str) -> Dict[str, list]:
    """
    Scan directory for files, categorizing them by type.
    
    Args:
        directory: Path to directory
        
    Returns:
        Dictionary with keys 'images', 'videos', 'other', each containing a list of file paths
    """
    result = {
        'images': [],
        'videos': [],
        'other': []
    }
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            if is_image_file(file_path):
                result['images'].append(file_path)
            elif is_video_file(file_path):
                result['videos'].append(file_path)
            else:
                result['other'].append(file_path)
    
    return result


def process_in_parallel(files: list, process_func, threads: int = None) -> list:
    """
    Process a list of files in parallel.
    
    Args:
        files: List of file paths
        process_func: Function to process each file
        threads: Number of threads to use
        
    Returns:
        List of results
    """
    if threads is None:
        threads = os.cpu_count()
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_file = {executor.submit(process_func, file): file for file in files}
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
    
    return results