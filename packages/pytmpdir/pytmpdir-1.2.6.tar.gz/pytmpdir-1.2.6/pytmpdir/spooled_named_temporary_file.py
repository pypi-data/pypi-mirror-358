import logging
import os
from pathlib import Path

from .dir_setting import DirSetting
from .disk_file import DiskFile
from .memory_file import MemoryFile

logger = logging.getLogger(__name__)


class SpooledNamedTemporaryFile:
    def __init__(self, *args, **kwargs):
        self._dir = kwargs.pop("dir", DirSetting.tmpDirPath)
        self._max_size = kwargs.pop("max_size", 0)
        self._mode = kwargs.pop("mode", "w+b")
        self._memory_file = MemoryFile()
        self._disk_file = None
        self._rolled = False
        self._closed = False
        self._name_called = False

    def seek(self, offset, whence=0):
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        if self._rolled:
            return self._disk_file.seek(offset, whence)

        return self._memory_file.seek(offset, whence)

    def write(self, data):
        if self._closed:
            raise ValueError("I/O operation on closed file.")
        if self._name_called and self._disk_file:
            self._disk_file.ensure_open()

        if isinstance(data, str):
            data = data.encode()

        if self._rolled:
            bytes_written = self._disk_file.write(data)
            assert bytes_written == len(
                data
            ), f"Disk write size mismatch. Expected {len(data)}, wrote {bytes_written}"
            return bytes_written

        # Check if we need to rollover
        current_pos = self._memory_file.tell()
        if self._max_size and (current_pos + len(data) > self._max_size):
            self.rollover()
            bytes_written = self._disk_file.write(data)
            assert bytes_written == len(
                data
            ), f"Post-rollover write size mismatch. Expected {len(data)}, wrote {bytes_written}"
            return bytes_written

        # Write to memory file
        bytes_written = self._memory_file.write(data)
        assert bytes_written == len(
            data
        ), f"Memory write size mismatch. Expected {len(data)}, wrote {bytes_written}"
        return bytes_written

    def read(self, size=-1):
        if self._closed:
            raise ValueError("I/O operation on closed file.")
        if self._name_called and self._disk_file:
            self._disk_file.ensure_open()

        if self._rolled:
            return self._disk_file.read(size)

        return self._memory_file.read(size)

    def close(self):
        if self._closed:
            return

        if self._disk_file:
            self._disk_file.close()

        self._memory_file.close()
        self._closed = True

    def rollover(self):
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        if self._rolled:
            return

        content = self._memory_file.getvalue()
        current_pos = self._memory_file.tell()

        self._disk_file = DiskFile(self._dir, self._mode)
        self._disk_file.initialize_with_content(content, current_pos)
        self._rolled = True

    @property
    def name(self):
        if self._name_called:
            # If file is closed, reopen it
            if self._disk_file and not self._disk_file._file:
                self._disk_file.ensure_open()
            return str(self._disk_file.path)

        if not self._rolled and (
            self._max_size == 0
            or len(self._memory_file.getvalue()) <= self._max_size
        ):
            self.rollover()

        self._name_called = True
        return str(self._disk_file.path)

    def moveToPath(self, path: Path):
        if not self._rolled:
            self.rollover()

        self._disk_file.move_to_path(path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            if hasattr(self, "_disk_file") and self._disk_file:
                logger.debug("Cleaning up disk file in destructor")
                path = self._disk_file.path
                self._disk_file.close()

                if path and Path(path).exists():
                    logger.debug(f"Removing file {path} in destructor")
                    Path(path).unlink()

            if hasattr(self, "_memory_file"):
                self._memory_file.close()
        except Exception as e:
            logger.error(f"Error in destructor: {e}")
            pass

    def tell(self):
        if self._rolled:
            return self._disk_file.tell()
        return self._memory_file.tell()

    def flush(self):
        if self._rolled:
            self._disk_file.flush_and_sync()
        # Memory file doesn't need flushing

    def getvalue(self):
        if self._rolled:
            return self._disk_file.getvalue()
        return self._memory_file.getvalue()

    def truncate(self, size=None):
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        if self._rolled:
            return self._disk_file.truncate(size)

        return self._memory_file.truncate(size)
