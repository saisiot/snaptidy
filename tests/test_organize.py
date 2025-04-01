"""
Tests for the organize module.
"""

import os
import shutil
import tempfile
import unittest
import datetime
from unittest.mock import patch, MagicMock

from snaptidy import organize
from snaptidy import utils


class TestOrganize(unittest.TestCase):
    """Tests for the organize module."""
    
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create some test files
        self.file1 = os.path.join(self.temp_dir, "file1.jpg")
        self.file2 = os.path.join(self.temp_dir, "file2.jpg")
        self.file3 = os.path.join(self.temp_dir, "file3.mp4")
        self.file4 = os.path.join(self.temp_dir, "file4.txt")
        
        # Touch the files to create them
        for file_path in [self.file1, self.file2, self.file3, self.file4]:
            with open(file_path, "w") as f:
                f.write("Test content")
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    @patch('snaptidy.utils.extract_date')
    def test_get_target_folder_year(self, mock_extract_date):
        """Test get_target_folder function with year format."""
        # Mock extract_date to return a fixed date
        mock_date = datetime.datetime(2020, 5, 15)
        mock_extract_date.return_value = mock_date
        
        # Get target folder for year format
        folder = organize.get_target_folder(self.file1, "year")
        
        # Check result
        self.assertEqual(folder, "2020")
        mock_extract_date.assert_called_once_with(self.file1)
    
    @patch('snaptidy.utils.extract_date')
    def test_get_target_folder_yearmonth(self, mock_extract_date):
        """Test get_target_folder function with yearmonth format."""
        # Mock extract_date to return a fixed date
        mock_date = datetime.datetime(2020, 5, 15)
        mock_extract_date.return_value = mock_date
        
        # Get target folder for yearmonth format
        folder = organize.get_target_folder(self.file1, "yearmonth")
        
        # Check result
        self.assertEqual(folder, "202005")
        mock_extract_date.assert_called_once_with(self.file1)
    
    @patch('snaptidy.utils.extract_date')
    def test_organize_files_dry_run(self, mock_extract_date):
        """Test organize_files function in dry_run mode."""
        # Mock extract_date to return fixed dates
        mock_dates = {
            self.file1: datetime.datetime(2020, 5, 15),
            self.file2: datetime.datetime(2021, 7, 20),
            self.file3: datetime.datetime(2020, 12, 31),
            self.file4: datetime.datetime(2022, 1, 1)
        }
        mock_extract_date.side_effect = lambda file_path: mock_dates.get(file_path)
        
        # Organize files in dry_run mode
        files = [self.file1, self.file2, self.file3, self.file4]
        folder_counts, total_organized = organize.organize_files(
            self.temp_dir, files, "year", dry_run=True)
        
        # Check results
        self.assertEqual(total_organized, 4)
        self.assertEqual(len(folder_counts), 3)  # 3 different years
        self.assertEqual(folder_counts.get("2020", 0), 2)
        self.assertEqual(folder_counts.get("2021", 0), 1)
        self.assertEqual(folder_counts.get("2022", 0), 1)
        
        # All files should still be in the root directory
        root_files = [f for f in os.listdir(self.temp_dir) 
                     if os.path.isfile(os.path.join(self.temp_dir, f))]
        self.assertEqual(len(root_files), 4)
        
        # No year folders should exist
        year_folders = [d for d in os.listdir(self.temp_dir) 
                       if os.path.isdir(os.path.join(self.temp_dir, d))]
        self.assertEqual(len(year_folders), 0)
    
    @patch('snaptidy.utils.extract_date')
    def test_organize_files(self, mock_extract_date):
        """Test organize_files function."""
        # Mock extract_date to return fixed dates
        mock_dates = {
            self.file1: datetime.datetime(2020, 5, 15),
            self.file2: datetime.datetime(2021, 7, 20),
            self.file3: datetime.datetime(2020, 12, 31),
            self.file4: datetime.datetime(2022, 1, 1)
        }
        mock_extract_date.side_effect = lambda file_path: mock_dates.get(file_path)
        
        # Organize files
        files = [self.file1, self.file2, self.file3, self.file4]
        folder_counts, total_organized = organize.organize_files(
            self.temp_dir, files, "year", dry_run=False)
        
        # Check results
        self.assertEqual(total_organized, 4)
        self.assertEqual(len(folder_counts), 3)  # 3 different years
        
        # Year folders should exist
        year_folders = [d for d in os.listdir(self.temp_dir) 
                       if os.path.isdir(os.path.join(self.temp_dir, d))]
        self.assertEqual(len(year_folders), 3)
        self.assertIn("2020", year_folders)
        self.assertIn("2021", year_folders)
        self.assertIn("2022", year_folders)
        
        # Check file locations
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "2020", "file1.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "2021", "file2.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "2020", "file3.mp4")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "2022", "file4.txt")))
    
    @patch('snaptidy.utils.scan_directory')
    @patch('snaptidy.organize.organize_files')
    def test_run_organize(self, mock_organize_files, mock_scan_directory):
        """Test run function."""
        # Mock scan_directory to return fixed files
        mock_scan_directory.return_value = {
            'images': [self.file1, self.file2],
            'videos': [self.file3],
            'other': [self.file4]
        }
        
        # Mock organize_files to return fixed results
        mock_organize_files.return_value = ({"2020": 2, "2021": 1}, 3)
        
        # Run organize
        organize.run(self.temp_dir, date_format="year", dry_run=False)
        
        # Check that organize_files was called correctly
        mock_organize_files.assert_any_call(
            self.temp_dir, [self.file1, self.file2, self.file3], "year", False)
        
        # Also check that other files were organized
        mock_organize_files.assert_any_call(
            self.temp_dir, [self.file4], "year", False)


if __name__ == "__main__":
    unittest.main()