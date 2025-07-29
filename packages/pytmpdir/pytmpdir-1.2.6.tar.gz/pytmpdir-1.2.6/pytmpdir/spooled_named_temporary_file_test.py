import hashlib
import os
import random
import shutil
import tarfile
import tempfile
import unittest
from io import BytesIO
from zipfile import ZipFile, ZIP_STORED

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .spooled_named_temporary_file import SpooledNamedTemporaryFile


class TestSpooledNamedTemporaryFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))

    def calculate_md5(self, data):
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).hexdigest()

    def test_operations_after_name(self):
        print("Starting test_operations_after_name")
        with SpooledNamedTemporaryFile(dir=self.test_dir) as f:
            data1 = b"test data"
            data2 = b"more data"

            f.write(data1)
            print(f"Wrote first data, rolled: {f._rolled}")
            name = f.name  # Access name property
            print(f"Accessed name, rolled: {f._rolled}")
            f.write(data2)
            print(f"Wrote second data, rolled: {f._rolled}")
            f.seek(0)
            read_data = f.read()

            expected_data = data1 + data2
            written_md5 = self.calculate_md5(expected_data)
            read_md5 = self.calculate_md5(read_data)
            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch: written={written_md5}, read={read_md5}",
            )
        print("Completed test_operations_after_name")

    def test_cleanup_after_name(self):
        file_path = None
        with SpooledNamedTemporaryFile(dir=self.test_dir) as f:
            data = b"test data"
            written_md5 = self.calculate_md5(data)

            f.write(data)
            file_path = f.name
            self.assertTrue(os.path.exists(file_path))

            f.seek(0)
            read_data = f.read()
            read_md5 = self.calculate_md5(read_data)
            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch: written={written_md5}, read={read_md5}",
            )
        self.assertFalse(os.path.exists(file_path))
        print("Completed test_cleanup_after_name")

    def test_destructor_cleanup(self):
        file_path = None
        f = SpooledNamedTemporaryFile(dir=self.test_dir)
        data = b"test data"
        written_md5 = self.calculate_md5(data)

        f.write(data)
        file_path = f.name
        self.assertTrue(os.path.exists(file_path))

        f.seek(0)
        read_data = f.read()
        read_md5 = self.calculate_md5(read_data)
        self.assertEqual(
            written_md5,
            read_md5,
            f"MD5 mismatch: written={written_md5}, read={read_md5}",
        )

        del f
        self.assertFalse(os.path.exists(file_path))
        print("Completed test_destructor_cleanup")

    def test_basic_write_read(self):
        with SpooledNamedTemporaryFile(dir=self.test_dir) as f:
            data1 = b"test data"
            written_md5_1 = self.calculate_md5(data1)

            f.write(data1)
            f.seek(0)
            read_data_1 = f.read()
            read_md5_1 = self.calculate_md5(read_data_1)
            self.assertEqual(
                written_md5_1,
                read_md5_1,
                f"MD5 mismatch first write: written={written_md5_1}, read={read_md5_1}",
            )
            self.assertEqual(read_data_1, data1)

            # Should be able to write after read
            data2 = b" more"
            f.write(data2)
            f.seek(0)
            read_data_2 = f.read()

            expected_combined = data1 + data2
            written_md5_2 = self.calculate_md5(expected_combined)
            read_md5_2 = self.calculate_md5(read_data_2)
            self.assertEqual(
                written_md5_2,
                read_md5_2,
                f"MD5 mismatch combined write: written={written_md5_2}, read={read_md5_2}",
            )
            self.assertEqual(read_data_2, expected_combined)
        print("Completed test_basic_write_read")

    def test_rollover_on_size(self):
        print("Starting test_rollover_on_size with max_size=5")
        with SpooledNamedTemporaryFile(max_size=5, dir=self.test_dir) as f:
            data = b"test data"  # This will cause rollover
            written_md5 = self.calculate_md5(data)
            print(f"About to write {len(data)} bytes, max_size=5")

            f.write(data)
            print(f"After write, rolled: {f._rolled}")
            self.assertTrue(os.path.exists(f.name))
            f.seek(0)
            read_data = f.read()
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch after rollover: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, data)
        print("Completed test_rollover_on_size")

    def test_write_under_max_size(self):
        max_size = 100
        test_data = b"x" * (max_size - 10)  # Write less than max_size
        written_md5 = self.calculate_md5(test_data)

        with SpooledNamedTemporaryFile(
            max_size=max_size, dir=self.test_dir
        ) as f:
            f.write(test_data)
            f.seek(0)
            read_data = f.read()
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch under max size: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, test_data)
        print("Completed test_write_under_max_size")

    def test_write_force_rollover(self):
        max_size = 100
        test_data = b"x" * (max_size + 10)  # Write more than max_size
        written_md5 = self.calculate_md5(test_data)

        with SpooledNamedTemporaryFile(
            max_size=max_size, dir=self.test_dir
        ) as f:
            f.write(test_data)
            self.assertTrue(f._rolled)  # Should have rolled over
            f.seek(0)
            read_data = f.read()
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch forced rollover: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, test_data)
        print("Completed test_write_force_rollover")

    def test_multiple_writes_with_rollover(self):
        max_size = 50
        with SpooledNamedTemporaryFile(
            max_size=max_size, dir=self.test_dir
        ) as f:
            # Write before rollover
            data1 = b"first_data"
            f.write(data1)
            self.assertFalse(f._rolled)

            # Write that causes rollover
            data2 = b"x" * max_size
            f.write(data2)
            self.assertTrue(f._rolled)

            # Write after rollover
            data3 = b"last_data"
            f.write(data3)

            f.seek(0)
            read_data = f.read()

            expected_combined = data1 + data2 + data3
            written_md5 = self.calculate_md5(expected_combined)
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch multiple writes: written={written_md5}, read={read_md5}",
            )
            self.assertTrue(b"first_data" in read_data)
            self.assertTrue(b"last_data" in read_data)
        print("Completed test_multiple_writes_with_rollover")

    def test_partial_reads(self):
        with SpooledNamedTemporaryFile(dir=self.test_dir) as f:
            data1 = b"test_data"
            written_md5_1 = self.calculate_md5(data1)

            f.write(data1)
            f.seek(0)
            partial = f.read(4)
            partial_md5 = self.calculate_md5(partial)
            expected_partial_md5 = self.calculate_md5(b"test")
            self.assertEqual(
                partial_md5,
                expected_partial_md5,
                f"MD5 mismatch partial read: expected={expected_partial_md5}, read={partial_md5}",
            )
            self.assertEqual(partial, b"test")

            # Write after partial read
            data2 = b"_more"
            f.write(data2)
            f.seek(0)
            read_data = f.read()

            expected_combined = b"test_more"
            written_md5_2 = self.calculate_md5(expected_combined)
            read_md5_2 = self.calculate_md5(read_data)
            self.assertEqual(
                written_md5_2,
                read_md5_2,
                f"MD5 mismatch after partial read write: written={written_md5_2}, read={read_md5_2}",
            )
            self.assertEqual(read_data, expected_combined)
        print("Completed test_partial_reads")

    def test_seek_operations(self):
        with SpooledNamedTemporaryFile(max_size=100, dir=self.test_dir) as f:
            initial_data = b"0123456789"
            f.write(initial_data)
            f.seek(5)
            partial = f.read(2)

            partial_md5 = self.calculate_md5(partial)
            expected_partial_md5 = self.calculate_md5(b"56")
            self.assertEqual(
                partial_md5,
                expected_partial_md5,
                f"MD5 mismatch seek read: expected={expected_partial_md5}, read={partial_md5}",
            )
            self.assertEqual(partial, b"56")

            # Write at current position
            f.write(b"XX")
            f.seek(0)
            read_data = f.read()

            expected_final = b"0123456XX9"
            written_md5 = self.calculate_md5(expected_final)
            read_md5 = self.calculate_md5(read_data)
            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch seek operations: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, expected_final)
        print("Completed test_seek_operations")

    def test_cleanup_after_write(self):
        file_path = None
        with SpooledNamedTemporaryFile(dir=self.test_dir) as tmpFile:
            data = b"test content"
            written_md5 = self.calculate_md5(data)

            tmpFile.write(data)
            file_path = tmpFile.name
            self.assertTrue(os.path.exists(file_path))

            tmpFile.seek(0)
            read_data = tmpFile.read()
            read_md5 = self.calculate_md5(read_data)
            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch cleanup test: written={written_md5}, read={read_md5}",
            )
        self.assertFalse(os.path.exists(file_path))
        print("Completed test_cleanup_after_write")

    def test_tar_archive_lifecycle(self):
        with SpooledNamedTemporaryFile(dir=self.test_dir) as tmpFile:
            original_data = b"test content"
            original_md5 = self.calculate_md5(original_data)

            with tarfile.open(
                fileobj=tmpFile, mode="w", bufsize=1024 * 1024
            ) as tar:
                info = tarfile.TarInfo(name="test.txt")
                info.size = len(original_data)
                tar.addfile(info, BytesIO(original_data))

            self.assertGreater(
                os.stat(tmpFile.name).st_size,
                0,
                "Tar archive file size should not be zero",
            )
            with tarfile.open(tmpFile.name, "r") as tar:
                member = tar.getmember("test.txt")
                extracted_data = tar.extractfile(member).read()
                extracted_md5 = self.calculate_md5(extracted_data)

                self.assertEqual(
                    original_md5,
                    extracted_md5,
                    f"MD5 mismatch tar archive: original={original_md5}, extracted={extracted_md5}",
                )
                self.assertEqual(extracted_data, original_data)
        print("Completed test_tar_archive_lifecycle")

    def test_zip_archive_lifecycle(self):
        with SpooledNamedTemporaryFile(dir=self.test_dir) as tmpFile:
            original_data = "test content"
            original_md5 = self.calculate_md5(original_data)

            with ZipFile(tmpFile, "w", compression=ZIP_STORED) as zip:
                zip.writestr("test.txt", original_data)

            tmpFile.seek(0)
            self.assertGreater(
                os.stat(tmpFile.name).st_size,
                0,
                "Zip archive file size should not be zero",
            )
            with ZipFile(tmpFile.name, "r") as zip:
                extracted_data = zip.read("test.txt")
                extracted_md5 = self.calculate_md5(extracted_data)

                self.assertEqual(
                    original_md5,
                    extracted_md5,
                    f"MD5 mismatch zip archive: original={original_md5}, extracted={extracted_md5}",
                )
                self.assertEqual(extracted_data, b"test content")
        print("Completed test_zip_archive_lifecycle")

    def test_multiple_files_archive(self):
        files = {
            "file1.txt": b"content1",
            "file2.txt": b"content2",
            "file3.txt": b"content3",
        }

        # Calculate MD5s for original data
        original_md5s = {
            filename: self.calculate_md5(content)
            for filename, content in files.items()
        }

        with SpooledNamedTemporaryFile(dir=self.test_dir) as tmpFile:
            with tarfile.open(
                fileobj=tmpFile, mode="w", bufsize=1024 * 1024
            ) as tar:
                for filename, content in files.items():
                    info = tarfile.TarInfo(name=filename)
                    info.size = len(content)
                    tar.addfile(info, BytesIO(content))

            self.assertGreater(
                os.stat(tmpFile.name).st_size,
                0,
                "Multiple files tar archive size should not be zero",
            )

            with tarfile.open(name=tmpFile.name, mode="r") as tar:
                for filename, expected_content in files.items():
                    member = tar.getmember(filename)
                    extracted_data = tar.extractfile(member).read()
                    extracted_md5 = self.calculate_md5(extracted_data)

                    self.assertEqual(
                        original_md5s[filename],
                        extracted_md5,
                        f"MD5 mismatch {filename}: original={original_md5s[filename]}, extracted={extracted_md5}",
                    )
                    self.assertEqual(extracted_data, expected_content)
        print("Completed test_multiple_files_archive")

    def test_overwrite_in_middle(self):
        with SpooledNamedTemporaryFile(dir=self.test_dir) as f:
            f.write(b"0123456789")
            f.seek(5)
            f.write(b"XXX")
            f.seek(0)
            read_data = f.read()

            expected_data = b"01234XXX89"
            written_md5 = self.calculate_md5(expected_data)
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch overwrite: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, expected_data)
        print("Completed test_overwrite_in_middle")

    def test_truncate_memory_file(self):
        with SpooledNamedTemporaryFile(max_size=100, dir=self.test_dir) as f:
            f.write(b"0123456789")
            new_size = f.truncate(5)
            self.assertEqual(new_size, 5)
            f.seek(0)
            read_data = f.read()

            expected_data = b"01234"
            written_md5 = self.calculate_md5(expected_data)
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch truncate memory: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, expected_data)
        print("Completed test_truncate_memory_file")

    def test_truncate_disk_file(self):
        with SpooledNamedTemporaryFile(max_size=5, dir=self.test_dir) as f:
            f.write(b"0123456789")  # This will cause rollover
            new_size = f.truncate(5)
            self.assertEqual(new_size, 5)
            f.seek(0)
            read_data = f.read()

            expected_data = b"01234"
            written_md5 = self.calculate_md5(expected_data)
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch truncate disk: written={written_md5}, read={read_md5}",
            )
            self.assertEqual(read_data, expected_data)
        print("Completed test_truncate_disk_file")

    def test_truncate_extend(self):
        with SpooledNamedTemporaryFile(dir=self.test_dir) as f:
            f.write(b"0123456789")
            new_size = f.truncate(15)
            self.assertEqual(new_size, 15)
            f.seek(0)
            read_data = f.read()

            expected_data = b"0123456789" + b"\x00" * 5
            written_md5 = self.calculate_md5(expected_data)
            read_md5 = self.calculate_md5(read_data)

            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch truncate extend: written={written_md5}, read={read_md5}",
            )
            # First 10 bytes should be original content
            self.assertEqual(read_data[:10], b"0123456789")
            # Remaining bytes should be zeros
            self.assertEqual(read_data[10:], b"\x00" * 5)
        print("Completed test_truncate_extend")

    def test_large_file_500mb(self):
        print("Starting test_large_file_500mb")
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = 500 * 1024 * 1024  # 500MB
        chunk_data = b"X" * chunk_size
        chunk_md5 = self.calculate_md5(chunk_data)

        with SpooledNamedTemporaryFile(max_size=1024, dir=self.test_dir) as f:
            # Write 500MB in 1MB chunks and calculate MD5 of all written data
            write_hasher = hashlib.md5()
            chunks_written = 0
            for i in range(total_size // chunk_size):
                f.write(chunk_data)
                write_hasher.update(chunk_data)
                chunks_written += 1
            written_md5 = write_hasher.hexdigest()

            # Verify file was rolled to disk due to size
            self.assertTrue(f._rolled)

            # Verify file size
            file_size = os.stat(f.name).st_size
            self.assertEqual(file_size, total_size)

            # Test seeking and reading from different positions with MD5 verification
            f.seek(0)
            first_chunk = f.read(chunk_size)
            first_chunk_md5 = self.calculate_md5(first_chunk)
            self.assertEqual(
                chunk_md5,
                first_chunk_md5,
                f"MD5 mismatch first chunk: original={chunk_md5}, read={first_chunk_md5}",
            )
            self.assertEqual(first_chunk, chunk_data)

            # Read from middle
            middle_pos = total_size // 2
            f.seek(middle_pos)
            middle_chunk = f.read(chunk_size)
            middle_chunk_md5 = self.calculate_md5(middle_chunk)
            self.assertEqual(
                chunk_md5,
                middle_chunk_md5,
                f"MD5 mismatch middle chunk: original={chunk_md5}, read={middle_chunk_md5}",
            )
            self.assertEqual(middle_chunk, chunk_data)

            # Read from end
            f.seek(total_size - chunk_size)
            last_chunk = f.read(chunk_size)
            last_chunk_md5 = self.calculate_md5(last_chunk)
            self.assertEqual(
                chunk_md5,
                last_chunk_md5,
                f"MD5 mismatch last chunk: original={chunk_md5}, read={last_chunk_md5}",
            )
            self.assertEqual(last_chunk, chunk_data)

            # Read entire file and calculate MD5 of all read data
            f.seek(0)
            read_hasher = hashlib.md5()
            while True:
                read_chunk = f.read(chunk_size)
                if not read_chunk:
                    break
                read_hasher.update(read_chunk)
            read_md5 = read_hasher.hexdigest()

            # Compare MD5 checksums of written vs read data
            self.assertEqual(
                written_md5,
                read_md5,
                f"MD5 mismatch entire file: written={written_md5}, read={read_md5}",
            )
        print("Completed test_large_file_500mb")

    def test_rollover_robustness_random_sizes(self):
        TEST_COUNT = 10
        for rollover_threshold in range(64 * 1024, 2 * 1024 * 1024, 64 * 1024):
            random.seed(rollover_threshold)  # For reproducible tests

            for test_num in range(TEST_COUNT):
                # Generate random size: 50% below threshold, 50% above
                if test_num < (TEST_COUNT / 2):
                    # Below threshold: 1 to threshold-1 bytes
                    data_size = random.randint(1, rollover_threshold - 1)
                else:
                    # Above threshold: threshold+1 to threshold*3 bytes
                    data_size = random.randint(
                        rollover_threshold + 1, rollover_threshold * 3
                    )

                print(
                    f"Testing"
                    f" rollover_threshold={rollover_threshold},"
                    f" data_size={data_size},"
                )

                # Generate random data
                test_data = bytes(
                    [random.randint(0, 255) for _ in range(data_size)]
                )
                expected_md5 = self.calculate_md5(test_data)

                with SpooledNamedTemporaryFile(
                    max_size=rollover_threshold, dir=self.test_dir
                ) as f:
                    f.write(test_data)

                    # Verify rollover state
                    if data_size > rollover_threshold:
                        self.assertTrue(
                            f._rolled,
                            f"Test {test_num}:"
                            f" rollover_threshold={rollover_threshold},"
                            f" Should have rolled over for size {data_size}",
                        )
                    else:
                        self.assertFalse(
                            f._rolled,
                            f"Test {test_num}:"
                            f" rollover_threshold={rollover_threshold},"
                            f" Should not have rolled over for size {data_size}",
                        )

                    # Test read integrity
                    f.seek(0)
                    read_data = f.read()
                    read_md5 = self.calculate_md5(read_data)

                    self.assertEqual(
                        expected_md5,
                        read_md5,
                        f"Test {test_num}:"
                        f" rollover_threshold={rollover_threshold},"
                        f" MD5 mismatch for size {data_size}:"
                        f" expected={expected_md5}, read={read_md5}",
                    )
                    self.assertEqual(
                        len(read_data),
                        data_size,
                        f"Test {test_num}:"
                        f" rollover_threshold={rollover_threshold},"
                        f" Size mismatch for {data_size} bytes",
                    )
        print("Completed test_rollover_robustness_random_sizes")

    def test_rollover_incremental_boundary(self):
        rollover_threshold = 5 * 1024 * 102

        for i in range(10):
            # Test sizes: 5 bytes before threshold, 5 bytes after
            # i=0: size=95, i=1: size=96, ..., i=4: size=99 (before threshold)
            # i=5: size=101, i=6: size=102, ..., i=9: size=105 (after threshold)
            if i < 5:
                data_size = rollover_threshold - 5 + i
            else:
                data_size = rollover_threshold + 1 + (i - 5)

            # Generate test data - use pattern that's easy to verify
            test_data = bytes([(j % 256) for j in range(data_size)])
            expected_md5 = self.calculate_md5(test_data)

            with SpooledNamedTemporaryFile(
                max_size=rollover_threshold, dir=self.test_dir
            ) as f:
                f.write(test_data)

                # Verify rollover state
                if data_size > rollover_threshold:
                    self.assertTrue(
                        f._rolled,
                        f"Boundary test {i}: Should have rolled over for size {data_size}",
                    )
                else:
                    self.assertFalse(
                        f._rolled,
                        f"Boundary test {i}: Should not have rolled over for size {data_size}",
                    )

                # Test read integrity
                f.seek(0)
                read_data = f.read()
                read_md5 = self.calculate_md5(read_data)

                self.assertEqual(
                    expected_md5,
                    read_md5,
                    f"Boundary test {i}: MD5 mismatch for size {data_size}: expected={expected_md5}, read={read_md5}",
                )
                self.assertEqual(
                    len(read_data),
                    data_size,
                    f"Boundary test {i}: Size mismatch for {data_size} bytes",
                )
        print("Completed test_rollover_incremental_boundary")

    @unittest.skipUnless(PSUTIL_AVAILABLE, "psutil not available")
    def test_memory_usage_1gb_file(self):
        print("Starting test_memory_usage_1gb_file")
        
        # Get current process
        process = psutil.Process()
        
        # Measure initial memory
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = 1024 * 1024 * 1024  # 1GB
        max_size_threshold = 10 * 1024 * 1024  # 10MB threshold for rollover
        
        # Create test data chunk
        chunk_data = b"A" * chunk_size
        
        with SpooledNamedTemporaryFile(max_size=max_size_threshold, dir=self.test_dir) as f:
            # Write first few chunks and measure memory before rollover
            for i in range(5):  # Write 5MB, still under threshold
                f.write(chunk_data)
            
            pre_rollover_memory = process.memory_info().rss / (1024 * 1024)
            print(f"Memory after 5MB (before rollover): {pre_rollover_memory:.2f} MB")
            self.assertFalse(f._rolled, "Should not have rolled over yet")
            
            # Write more chunks to trigger rollover
            for i in range(10):  # Write another 10MB, should trigger rollover
                f.write(chunk_data)
            
            post_rollover_memory = process.memory_info().rss / (1024 * 1024)
            print(f"Memory after rollover: {post_rollover_memory:.2f} MB")
            self.assertTrue(f._rolled, "Should have rolled over to disk")
            
            # Write remaining chunks to reach 1GB
            chunks_written = 15
            total_chunks = total_size // chunk_size
            
            for i in range(chunks_written, total_chunks):
                f.write(chunk_data)
                
                # Check memory every 100MB
                if (i + 1) % 100 == 0:
                    current_memory = process.memory_info().rss / (1024 * 1024)
                    written_mb = (i + 1)
                    print(f"Memory after {written_mb}MB written: {current_memory:.2f} MB")
            
            final_memory = process.memory_info().rss / (1024 * 1024)
            print(f"Final memory after 1GB written: {final_memory:.2f} MB")
            
            # Verify file size
            file_size = os.stat(f.name).st_size
            self.assertEqual(file_size, total_size, "File size should be 1GB")
            
            # Memory should not have grown significantly after rollover
            # Allow for some variance but it shouldn't grow by more than 100MB
            memory_growth = final_memory - post_rollover_memory
            print(f"Memory growth after rollover: {memory_growth:.2f} MB")
            
            self.assertLess(
                memory_growth, 100,
                f"Memory grew too much after rollover: {memory_growth:.2f} MB. "
                f"This suggests data is being kept in memory instead of written to disk."
            )
            
            # Verify we can read the data correctly
            f.seek(0)
            first_chunk = f.read(chunk_size)
            self.assertEqual(first_chunk, chunk_data, "First chunk should match written data")
            
            # Seek to end and verify last chunk
            f.seek(total_size - chunk_size)
            last_chunk = f.read(chunk_size)
            self.assertEqual(last_chunk, chunk_data, "Last chunk should match written data")
        
        print("Completed test_memory_usage_1gb_file")


if __name__ == "__main__":
    unittest.main()