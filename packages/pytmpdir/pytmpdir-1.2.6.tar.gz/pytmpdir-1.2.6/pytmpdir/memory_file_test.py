import unittest
from memory_file import MemoryFile


class TestMemoryFile(unittest.TestCase):
    def setUp(self):
        self.file = MemoryFile()

    def tearDown(self):
        self.file.close()

    def test_write_read_basic(self):
        self.file.write(b"test data")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"test data")

    def test_write_after_read(self):
        # Initial write and read
        self.file.write(b"initial data")
        self.file.seek(0)
        self.file.read()

        # Should be able to write after read
        self.file.write(b" more data")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"initial data more data")

    def test_string_handling(self):
        self.file.write("test string")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"test string")

    def test_multiple_writes(self):
        self.file.write(b"first ")
        self.file.write(b"second")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"first second")

    def test_seek_operations(self):
        self.file.write(b"0123456789")
        self.file.seek(5)
        content = self.file.read()
        self.assertEqual(content, b"56789")

        # Write at current position
        self.file.write(b"XXX")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"0123456789XXX")

    def test_closed_operations(self):
        self.file.close()
        with self.assertRaises(ValueError):
            self.file.write(b"test")
        with self.assertRaises(ValueError):
            self.file.read()
        with self.assertRaises(ValueError):
            self.file.seek(0)

    def test_tell_position(self):
        self.file.write(b"test")
        self.assertEqual(self.file.tell(), 4)
        self.file.seek(2)
        self.assertEqual(self.file.tell(), 2)

    def test_empty_read(self):
        content = self.file.read()
        self.assertEqual(content, b"")
        self.file.write(b"test")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"test")

    def test_getvalue(self):
        self.file.write(b"test data")
        self.assertEqual(self.file.getvalue(), b"test data")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"test data")

        # Should be able to write after getvalue
        self.file.write(b" more")
        self.assertEqual(self.file.getvalue(), b"test data more")

    def test_partial_reads(self):
        self.file.write(b"test_data")
        self.file.seek(0)
        partial = self.file.read(4)
        self.assertEqual(partial, b"test")

        # Write after partial read
        self.file.write(b"_more")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"test_more")

    def test_overwrite_in_middle(self):
        self.file.write(b"0123456789")
        self.file.seek(5)
        self.file.write(b"XXX")
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"01234XXX89")

    def test_truncate_with_size(self):
        self.file.write(b"0123456789")
        new_size = self.file.truncate(5)
        self.assertEqual(new_size, 5)
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"01234")

    def test_truncate_without_size(self):
        self.file.write(b"0123456789")
        self.file.seek(5)
        new_size = self.file.truncate()
        self.assertEqual(new_size, 5)
        self.file.seek(0)
        content = self.file.read()
        self.assertEqual(content, b"01234")

    def test_truncate_extend(self):
        self.file.write(b"0123456789")
        new_size = self.file.truncate(15)
        self.assertEqual(new_size, 15)
        self.file.seek(0)
        content = self.file.read()
        # First 10 bytes should be original content
        self.assertEqual(content[:10], b"0123456789")
        # Remaining bytes should be zeros
        self.assertEqual(content[10:], b"\x00" * 5)


if __name__ == "__main__":
    unittest.main()
