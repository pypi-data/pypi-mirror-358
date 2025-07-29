import os
import platform
import shutil
import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile

_isWindows = platform.system() == "Windows"


class DiskFile:
    def __init__(self, dir_path, mode="w+b"):
        self._dir = dir_path
        self._mode = mode
        self._file = None
        self._path = None
        self._closed = False

    def initialize_with_content(self, content, position):
        if not content:
            content = b""
        content_size = len(content)
        if _isWindows:
            temp_path = Path(self._dir) / f"spooled_{uuid.uuid4()}.tmp"
            self._file = open(temp_path, "w+b")
        else:
            temp_file = NamedTemporaryFile(
                mode="w+b", dir=self._dir, delete=False
            )
            temp_path = temp_file.name
            self._file = temp_file

        self._path = temp_path
        self._file.write(content)
        self._file.flush()
        if hasattr(os, "fsync"):
            os.fsync(self._file.fileno())
        self._file.seek(position)
        written_size = os.path.getsize(self._path)
        assert (
            written_size == content_size
        ), f"File size mismatch. Expected {content_size}, got {written_size}"
        return self._path

    def ensure_open(self):
        if not self._file:
            # Use r+b mode when reopening existing files to avoid truncation
            mode = (
                "r+b"
                if self._path and Path(self._path).exists()
                else self._mode
            )
            self._file = open(self._path, mode)
            self._file.seek(0)

    def flush_and_sync(self):
        if self._file:
            self._file.flush()
            if hasattr(os, "fsync"):
                os.fsync(self._file.fileno())

    def ensure_closed(self):
        if self._file:
            self.flush_and_sync()
            self._file.close()
            self._file = None

    def close(self, delete_file=True):
        if self._closed:
            return

        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None

        self._closed = True

        if delete_file and self._path and Path(self._path).exists():
            Path(self._path).unlink()

    def move_to_path(self, path: Path):
        if not self._file:
            return

        self._file.flush()
        if hasattr(os, "fsync"):
            os.fsync(self._file.fileno())
        self._file.close()
        self._file = None

        if _isWindows:
            shutil.copy2(self._path, path)
            return

        shutil.move(self._path, path)

    def seek(self, offset, whence=0):
        self.ensure_open()
        return self._file.seek(offset, whence)

    def write(self, data):
        self.ensure_open()
        bytes_written = self._file.write(data)
        assert bytes_written == len(
            data
        ), f"Write size mismatch. Expected {len(data)}, wrote {bytes_written}"
        return bytes_written

    def read(self, size=-1):
        self.ensure_open()
        return self._file.read(size)

    def tell(self):
        self.ensure_open()
        return self._file.tell()

    def getvalue(self):
        self.ensure_open()
        current_pos = self._file.tell()
        self._file.seek(0)
        content = self._file.read()
        self._file.seek(current_pos)
        return content

    @property
    def closed(self):
        return self._closed

    @property
    def path(self):
        return self._path

    def truncate(self, size=None):
        self.ensure_open()
        current_position = self._file.tell()
        new_size = self._file.truncate(size)
        # Python's truncate doesn't change the file position
        self._file.seek(min(current_position, new_size))
        return new_size

    def __del__(self):
        try:
            if hasattr(self, "_file") and self._file:
                self._file.close()

            if hasattr(self, "_path") and self._path:
                if Path(self._path).exists():
                    Path(self._path).unlink()
        except:
            pass
