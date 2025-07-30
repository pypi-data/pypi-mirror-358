import os
import sys
import tempfile
import unittest
from pathlib import Path
from io import StringIO

from jinnang.io.system import (
    suppress_c_stdout_stderr,
    suppress_stdout_stderr,
    get_worker_num_for_io_bounded_task,
    create_relative_symlink,
    safe_delete,
    safe_move,
    copy_with_meta,
    inplace_overwrite_meta
)


class TestSystemIO(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for file operations
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test files
        self.test_file = self.temp_path / "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")
            
        # Create a subdirectory
        self.sub_dir = self.temp_path / "subdir"
        self.sub_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_suppress_c_stdout_stderr(self):
        # Test suppressing C-level stdout
        with suppress_c_stdout_stderr(suppress_stdout=True, suppress_stderr=False):
            # This would normally print to stdout at C level
            # Since we can't easily test C-level output, we'll just ensure the context manager runs without errors
            pass
        
        # Test suppressing C-level stderr
        with suppress_c_stdout_stderr(suppress_stdout=False, suppress_stderr=True):
            # This would normally print to stderr at C level
            pass
        
        # Test suppressing both
        with suppress_c_stdout_stderr(suppress_stdout=True, suppress_stderr=True):
            pass
    
    def test_suppress_stdout_stderr(self):
        # Test suppressing Python-level stdout
        original_stdout = sys.stdout
        with suppress_stdout_stderr(suppress_stdout=True, suppress_stderr=False):
            print("This should be suppressed")
            self.assertNotEqual(sys.stdout, original_stdout)
        self.assertEqual(sys.stdout, original_stdout)  # Check stdout is restored
        
        # Test suppressing Python-level stderr
        original_stderr = sys.stderr
        with suppress_stdout_stderr(suppress_stdout=False, suppress_stderr=True):
            sys.stderr.write("This should be suppressed")
            self.assertNotEqual(sys.stderr, original_stderr)
        self.assertEqual(sys.stderr, original_stderr)  # Check stderr is restored
        
        # Test suppressing both
        with suppress_stdout_stderr(suppress_stdout=True, suppress_stderr=True):
            print("This should be suppressed")
            sys.stderr.write("This should be suppressed")
            self.assertNotEqual(sys.stdout, original_stdout)
            self.assertNotEqual(sys.stderr, original_stderr)
        self.assertEqual(sys.stdout, original_stdout)  # Check stdout is restored
        self.assertEqual(sys.stderr, original_stderr)  # Check stderr is restored
    
    def test_get_worker_num_for_io_bounded_task(self):
        # Test with user-defined value within bounds
        self.assertEqual(get_worker_num_for_io_bounded_task(5), 5)
        
        # Test with user-defined value below minimum
        self.assertEqual(get_worker_num_for_io_bounded_task(0), 1)
        
        # Test with user-defined value above maximum
        self.assertEqual(get_worker_num_for_io_bounded_task(50), 32)
        
        # Test with no user-defined value (auto-calculation)
        # We can't assert exact value as it depends on the system's CPU count
        worker_num = get_worker_num_for_io_bounded_task()
        self.assertGreaterEqual(worker_num, 4)  # Should be at least 4
        self.assertLessEqual(worker_num, 32)    # Should not exceed 32
    
    def test_create_relative_symlink(self):
        # Create a symlink to the test file
        link_folder = self.temp_path / "links"
        create_relative_symlink(str(self.test_file), str(link_folder))
        
        # Check if the symlink was created
        link_path = link_folder / self.test_file.name
        self.assertTrue(link_path.exists())
        self.assertTrue(link_path.is_symlink())
        
        # Check if the symlink points to the correct file
        self.assertEqual(os.readlink(link_path), os.path.relpath(self.test_file, link_folder))
        
        # Check if the content is accessible through the symlink
        with open(link_path, "r") as f:
            self.assertEqual(f.read(), "Test content")
        
        # Test with invalid inputs
        with self.assertRaises(AssertionError):
            create_relative_symlink("", str(link_folder))
        
        with self.assertRaises(AssertionError):
            create_relative_symlink(str(self.test_file), "")
    
    def test_safe_delete(self):
        # Create a file to delete
        file_to_delete = self.temp_path / "delete_me.txt"
        with open(file_to_delete, "w") as f:
            f.write("Delete me")
        
        # Test deleting an existing file
        self.assertTrue(file_to_delete.exists())
        safe_delete(file_to_delete)
        self.assertFalse(file_to_delete.exists())
        
        # Test deleting a non-existent file (should not raise an error)
        safe_delete(file_to_delete)  # File is already deleted
        
        # Test deleting a file with permission error (using mock)
        from unittest.mock import patch
        test_file = self.temp_path / "test_perm.txt"
        with open(test_file, "w") as f:
            f.write("Test file")
        
        with patch('os.remove', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(PermissionError):
                safe_delete(test_file)
    
    def test_safe_move(self):
        # Create a file to move
        src_file = self.temp_path / "move_me.txt"
        with open(src_file, "w") as f:
            f.write("Move me")
        
        # Test moving to a new location
        dst_file = self.temp_path / "moved.txt"
        self.assertTrue(safe_move(str(src_file), str(dst_file)))
        self.assertFalse(src_file.exists())
        self.assertTrue(dst_file.exists())
        with open(dst_file, "r") as f:
            self.assertEqual(f.read(), "Move me")
        
        # Test moving to a directory (should use the original filename)
        src_file = self.temp_path / "move_to_dir.txt"
        with open(src_file, "w") as f:
            f.write("Move to directory")
        
        self.assertTrue(safe_move(str(src_file), str(self.sub_dir)))
        self.assertFalse(src_file.exists())
        self.assertTrue((self.sub_dir / "move_to_dir.txt").exists())
        
        # Test moving a non-existent file
        non_existent = self.temp_path / "non_existent.txt"
        self.assertFalse(safe_move(str(non_existent), str(self.sub_dir)))
        
        # Test with invalid inputs
        self.assertFalse(safe_move("", str(self.sub_dir)))
        self.assertFalse(safe_move(str(dst_file), ""))
        
        # Test moving a directory (should fail)
        self.assertFalse(safe_move(str(self.sub_dir), str(self.temp_path / "new_dir")))
    
    def test_copy_with_meta(self):
        # Create a file to copy
        src_file = self.temp_path / "copy_me.txt"
        with open(src_file, "w") as f:
            f.write("Copy me with metadata")
        
        # Set access and modification times
        access_time = 1600000000  # Some timestamp
        mod_time = 1600000100     # Some timestamp
        os.utime(src_file, (access_time, mod_time))
        
        # Test copying to a new location
        dst_file = self.temp_path / "copied.txt"
        self.assertTrue(copy_with_meta(src_file, dst_file))
        self.assertTrue(src_file.exists())  # Original should still exist
        self.assertTrue(dst_file.exists())  # Copy should exist
        
        # Check content
        with open(dst_file, "r") as f:
            self.assertEqual(f.read(), "Copy me with metadata")

        # Check metadata (modification time)
        stat_dst = os.stat(dst_file)
        self.assertEqual(stat_dst.st_mtime, mod_time)
        
        # Check metadata (timestamps)
        src_stat = os.stat(src_file)
        dst_stat = os.stat(dst_file)
        self.assertEqual(dst_stat.st_mtime, src_stat.st_mtime)
        
        # Test copying to a non-existent directory (should create it)
        new_dir = self.temp_path / "new_dir"
        dst_file2 = new_dir / "copied.txt"
        self.assertTrue(copy_with_meta(src_file, dst_file2))
        self.assertTrue(dst_file2.exists())
        
        # Test with invalid inputs
        self.assertFalse(copy_with_meta("", dst_file))
        self.assertFalse(copy_with_meta(src_file, ""))
        
        # Test copying a non-existent file
        non_existent = self.temp_path / "non_existent.txt"
        self.assertFalse(copy_with_meta(non_existent, dst_file))
        
        # Test copying a directory (should fail)
        self.assertFalse(copy_with_meta(self.sub_dir, dst_file))
    
    def test_inplace_overwrite_meta(self):
        # Create source and target files
        src_file = self.temp_path / "source_meta.txt"
        target_file = self.temp_path / "target_meta.txt"
        
        with open(src_file, "w") as f:
            f.write("Source file")
        
        with open(target_file, "w") as f:
            f.write("Target file")
        
        # Set different timestamps for source
        access_time = 1600000000  # Some timestamp
        mod_time = 1600000100     # Some timestamp
        os.utime(src_file, (access_time, mod_time))
        
        # Set different timestamps for target
        os.utime(target_file, (1500000000, 1500000100))
        
        # Apply metadata from source to target
        inplace_overwrite_meta(src_file, target_file)
        
        # Check if timestamps were copied correctly
        src_stat = os.stat(src_file)
        target_stat = os.stat(target_file)
        
        self.assertEqual(target_stat.st_mtime, src_stat.st_mtime)
        self.assertEqual(target_stat.st_atime, src_stat.st_atime)
        
        # Content should remain unchanged
        with open(target_file, "r") as f:
            self.assertEqual(f.read(), "Target file")


if __name__ == "__main__":
    unittest.main()