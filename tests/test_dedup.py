"""
Tests for the dedup module.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from snaptidy import dedup


class TestDedup(unittest.TestCase):
    """Tests for the dedup module."""
    
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create some test files with identical content
        self.content1 = b"This is test content 1."
        self.content2 = b"This is different test content."
        
        self.file1 = os.path.join(self.temp_dir, "file1.txt")
        self.file2 = os.path.join(self.temp_dir, "file2.txt")  # Duplicate of file1
        self.file3 = os.path.join(self.temp_dir, "file3.txt")  # Unique content
        
        with open(self.file1, "wb") as f:
            f.write(self.content1)
        
        with open(self.file2, "wb") as f:
            f.write(self.content1)  # Same content as file1
        
        with open(self.file3, "wb") as f:
            f.write(self.content2)
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_duplicate_group(self):
        """Test DuplicateGroup class."""
        # Create a duplicate group
        group = dedup.DuplicateGroup(self.file1)
        group.add_duplicate(self.file2)
        
        # Check group properties
        self.assertEqual(group.original_file, self.file1)
        self.assertEqual(len(group.duplicates), 1)
        self.assertEqual(group.duplicates[0], self.file2)
        
        # Check get_all_files method
        all_files = group.get_all_files()
        self.assertEqual(len(all_files), 2)
        self.assertIn(self.file1, all_files)
        self.assertIn(self.file2, all_files)
        
        # Check get_total_size_to_recover method
        size_to_recover = group.get_total_size_to_recover()
        self.assertEqual(size_to_recover, len(self.content1))
    
    def test_find_exact_duplicates(self):
        """Test find_exact_duplicates function."""
        files = [self.file1, self.file2, self.file3]
        duplicate_groups = dedup.find_exact_duplicates(files, threads=1)
        
        # We should find one group of duplicates
        self.assertEqual(len(duplicate_groups), 1)
        
        # Get the first (and only) group
        hash_key = list(duplicate_groups.keys())[0]
        group = duplicate_groups[hash_key]
        
        # Check the group
        self.assertEqual(len(group.duplicates), 1)
        self.assertTrue(
            (group.original_file == self.file1 and group.duplicates[0] == self.file2) or
            (group.original_file == self.file2 and group.duplicates[0] == self.file1)
        )
    
    def test_remove_duplicates_dry_run(self):
        """Test remove_duplicates function in dry_run mode."""
        # Create a duplicate group
        group = dedup.DuplicateGroup(self.file1)
        group.add_duplicate(self.file2)
        
        # Remove duplicates in dry_run mode
        files_removed, bytes_recovered = dedup.remove_duplicates([group], dry_run=True)
        
        # Check results
        self.assertEqual(files_removed, 1)
        self.assertEqual(bytes_recovered, len(self.content1))
        
        # Both files should still exist
        self.assertTrue(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))
    
    def test_remove_duplicates(self):
        """Test remove_duplicates function."""
        # Create a duplicate group
        group = dedup.DuplicateGroup(self.file1)
        group.add_duplicate(self.file2)
        
        # Remove duplicates
        files_removed, bytes_recovered = dedup.remove_duplicates([group], dry_run=False)
        
        # Check results
        self.assertEqual(files_removed, 1)
        self.assertEqual(bytes_recovered, len(self.content1))
        
        # Original file should exist, duplicate should be gone
        self.assertTrue(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
    
    def test_run_dedup_dry_run(self):
        """Test run function in dry_run mode."""
        # Count files before deduplication
        files_before = len(os.listdir(self.temp_dir))
        
        # Run deduplication in dry_run mode
        dedup.run(self.temp_dir, sensitivity=0.9, dry_run=True, threads=1)
        
        # Count files after deduplication
        files_after = len(os.listdir(self.temp_dir))
        
        # File count should not change in dry_run mode
        self.assertEqual(files_before, files_after)
    
    def test_run_dedup(self):
        """Test run function."""
        # Count files before deduplication
        files_before = len(os.listdir(self.temp_dir))
        
        # Run deduplication
        dedup.run(self.temp_dir, sensitivity=0.9, dry_run=False, threads=1)
        
        # Count files after deduplication
        files_after = len(os.listdir(self.temp_dir))
        
        # We should have one less file (the duplicate)
        self.assertEqual(files_after, files_before - 1)
        
        # Check which files remain
        remaining_files = os.listdir(self.temp_dir)
        self.assertEqual(len(remaining_files), 2)
        
        # Make sure we still have one copy of each content
        contents = set()
        for filename in remaining_files:
            with open(os.path.join(self.temp_dir, filename), "rb") as f:
                contents.add(f.read())
        
        self.assertEqual(len(contents), 2)
        self.assertIn(self.content1, contents)
        self.assertIn(self.content2, contents)


if __name__ == "__main__":
    unittest.main()