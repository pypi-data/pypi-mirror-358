import platform
import shutil
import tempfile
import unittest
from pathlib import Path

from disk_file import DiskFile


class TestDiskFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_content = b"test content"
        self.disk_file = DiskFile(self.test_dir)

    def tearDown(self):
        if hasattr(self, "disk_file"):
            self.disk_file.close()
        shutil.rmtree(self.test_dir)

    def test_initialization_with_content(self):
        path = self.disk_file.initialize_with_content(self.test_content, 0)
        self.assertTrue(Path(path).exists())
        content = self.disk_file.read()
        self.assertEqual(content, self.test_content)

    def test_write_read_operations(self):
        self.disk_file.initialize_with_content(b"", 0)
        self.disk_file.write(b"test data")
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"test data")

        # Should be able to write after read
        self.disk_file.write(b" more")
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"test data more")

    def test_seek_operations(self):
        self.disk_file.initialize_with_content(b"0123456789", 0)
        self.disk_file.seek(5)
        content = self.disk_file.read()
        self.assertEqual(content, b"56789")

        # Write at current position
        self.disk_file.write(b"XXX")
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"0123456789XXX")

    def test_file_closing(self):
        path = self.disk_file.initialize_with_content(self.test_content, 0)
        self.disk_file.close()
        self.assertTrue(self.disk_file.closed)
        self.assertFalse(Path(path).exists())

    def test_move_to_path(self):
        self.disk_file.initialize_with_content(self.test_content, 0)
        target_path = Path(self.test_dir) / "moved_file.tmp"

        self.disk_file.move_to_path(target_path)
        self.assertTrue(target_path.exists())

        with open(target_path, "rb") as f:
            self.assertEqual(f.read(), self.test_content)

    def test_getvalue(self):
        self.disk_file.initialize_with_content(self.test_content, 0)
        self.disk_file.seek(5)  # Move position
        self.assertEqual(self.disk_file.getvalue(), self.test_content)

        # Should be able to write after getvalue
        self.disk_file.write(b"XXX")
        self.disk_file.seek(0)
        self.assertEqual(self.disk_file.getvalue(), b"test XXXtent")

    def test_tell_position(self):
        self.disk_file.initialize_with_content(b"test data", 0)
        self.disk_file.seek(4)
        self.assertEqual(self.disk_file.tell(), 4)
        self.disk_file.write(b"XX")
        self.assertEqual(self.disk_file.tell(), 6)

    def test_ensure_open(self):
        path = self.disk_file.initialize_with_content(self.test_content, 0)
        self.disk_file.close(delete_file=False)

        # Create new DiskFile instance pointing to same path
        new_disk_file = DiskFile(self.test_dir)
        new_disk_file._path = path
        new_disk_file.ensure_open()

        content = new_disk_file.read()
        self.assertEqual(content, self.test_content)

        # Should be able to write after read
        new_disk_file.write(b" more")
        new_disk_file.seek(0)
        self.assertEqual(new_disk_file.read(), self.test_content + b" more")
        new_disk_file.close()

    def test_multiple_writes(self):
        self.disk_file.initialize_with_content(b"", 0)
        self.disk_file.write(b"first ")
        self.disk_file.write(b"second")
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"first second")

    def test_cleanup_on_deletion(self):
        path = self.disk_file.initialize_with_content(self.test_content, 0)
        path_str = str(path)
        del self.disk_file
        self.assertFalse(Path(path_str).exists())

    def test_platform_specific_behavior(self):
        is_windows = platform.system() == "Windows"
        path = self.disk_file.initialize_with_content(self.test_content, 0)

        if is_windows:
            self.assertTrue("spooled_" in Path(path).name)
            self.assertTrue(path.name.endswith(".tmp"))
        else:
            self.assertTrue(Path(path).exists())

    def test_partial_reads(self):
        self.disk_file.initialize_with_content(b"test_data", 0)
        partial = self.disk_file.read(4)
        self.assertEqual(partial, b"test")

        # Should be able to write after partial read
        self.disk_file.write(b"_new")
        self.disk_file.seek(0)
        self.assertEqual(self.disk_file.read(), b"test_newa")

    def test_overwrite_in_middle(self):
        self.disk_file.initialize_with_content(b"0123456789", 0)
        self.disk_file.seek(5)
        self.disk_file.write(b"XXX")
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"01234XXX89")

    def test_truncate_with_size(self):
        self.disk_file.initialize_with_content(b"0123456789", 0)
        new_size = self.disk_file.truncate(5)
        self.assertEqual(new_size, 5)
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"01234")

    def test_truncate_without_size(self):
        self.disk_file.initialize_with_content(b"0123456789", 0)
        self.disk_file.seek(5)
        new_size = self.disk_file.truncate()
        self.assertEqual(new_size, 5)
        self.disk_file.seek(0)
        content = self.disk_file.read()
        self.assertEqual(content, b"01234")

    def test_truncate_extend(self):
        self.disk_file.initialize_with_content(b"0123456789", 0)
        new_size = self.disk_file.truncate(15)
        self.assertEqual(new_size, 15)
        self.disk_file.seek(0)
        content = self.disk_file.read()
        # First 10 bytes should be original content
        self.assertEqual(content[:10], b"0123456789")
        # Remaining bytes should be zeros
        self.assertEqual(content[10:], b"\x00" * 5)


if __name__ == "__main__":
    unittest.main()
