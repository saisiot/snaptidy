"""
Tests for the flatten module.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from snaptidy import flatten


class TestFlatten(unittest.TestCase):
    """Tests for the flatten module."""
    
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a nested directory structure
        os.makedirs(os.path.join(self.temp_dir, "subfolder1"))
        os.makedirs(os.path.join(self.temp_dir, "subfolder1", "nested"))
        os.makedirs(os.path.join(self.temp_dir, "subfolder2"))
        
        # Create some test files
        with open(os.path.join(self.temp_dir, "root_file.txt"), "w") as f:
            f.write("This is a file in the root directory.")
        
        with open(os.path.join(self.temp_dir, "subfolder1", "file1.txt"), "w") as f:
            f.write("This is a file in subfolder1.")
        
        with open(os.path.join(self.temp_dir, "subfolder1", "nested", "file2.txt"), "w") as f:
            f.write("This is a file in a nested folder.")
        
        with open(os.path.join(self.temp_dir, "subfolder2", "file3.txt"), "w") as f:
            f.write("This is a file in subfolder2.")
        
        # Create a duplicate filename across directories
        with open(os.path.join(self.temp_dir, "subfolder2", "root_file.txt"), "w") as f:
            f.write("This is a duplicate filename.")
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_all_files(self):
        """Test the get_all_files function."""
        files = flatten.get_all_files(self.temp_dir)
        self.assertEqual(len(files), 5)
    
    def test_get_unique_filename(self):
        """Test the get_unique_filename function."""
        original_name = "root_file.txt"
        unique_name = flatten.get_unique_filename(self.temp_dir, original_name)
        
        # The original file exists, so we should get a new name
        self.assertNotEqual(unique_name, original_name)
        self.assertTrue(unique_name.startswith("root_file_"))
        
        # Try with a file that doesn't exist
        new_name = "nonexistent_file.txt"
        unique_name = flatten.get_unique_filename(self.temp_dir, new_name)
        self.assertEqual(unique_name, new_name)
    
    def test_flatten_dry_run(self):
        """Test the flatten function in dry_run mode."""
        # Count files in root directory before flattening
        root_files_before = len([f for f in os.listdir(self.temp_dir) 
                                if os.path.isfile(os.path.join(self.temp_dir, f))])
        
        # Run flatten in dry_run mode
        flatten.run(self.temp_dir, dry_run=True)
        
        # Count files in root directory after flattening
        root_files_after = len([f for f in os.listdir(self.temp_dir) 
                               if os.path.isfile(os.path.join(self.temp_dir, f))])
        
        # File count should not change in dry_run mode
        self.assertEqual(root_files_before, root_files_after)
        
        # Subdirectories should still exist
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "subfolder1")))
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "subfolder2")))
    
    def test_flatten(self):
        """Test the flatten function."""
        # Run flatten
        flatten.run(self.temp_dir, dry_run=False)
        
        # All files should now be in the root directory
        root_files = [f for f in os.listdir(self.temp_dir) 
                     if os.path.isfile(os.path.join(self.temp_dir, f))]
        self.assertEqual(len(root_files), 5)
        
        # Subfolder1 should be gone (or empty)
        subfolder1_path = os.path.join(self.temp_dir, "subfolder1")
        subfolder1_exists = os.path.exists(subfolder1_path) and os.listdir(subfolder1_path)
        self.assertFalse(subfolder1_exists)
        
        # Subfolder2 should be gone (or empty)
        subfolder2_path = os.path.join(self.temp_dir, "subfolder2")
        subfolder2_exists = os.path.exists(subfolder2_path) and os.listdir(subfolder2_path)
        self.assertFalse(subfolder2_exists)
        
        # Check for renamed files
        renamed_files = [f for f in root_files if "_" in f]
        self.assertTrue(len(renamed_files) > 0)


if __name__ == "__main__":
    unittest.main()