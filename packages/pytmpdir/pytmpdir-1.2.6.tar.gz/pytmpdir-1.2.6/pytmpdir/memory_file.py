import io


class MemoryFile:
    def __init__(self):
        self._buffer = io.BytesIO()
        self._closed = False

    def seek(self, offset, whence=0):
        if self._closed:
            raise ValueError("I/O operation on closed file.")
        return self._buffer.seek(offset, whence)

    def write(self, data):
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        if isinstance(data, str):
            data = data.encode()

        bytes_written = self._buffer.write(data)
        assert bytes_written == len(
            data
        ), f"Write size mismatch. Expected {len(data)}, wrote {bytes_written}"
        return bytes_written

    def read(self, size=-1):
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        return self._buffer.read(size)

    def close(self):
        if self._closed:
            return
        self._buffer.close()
        self._closed = True

    def tell(self):
        return self._buffer.tell()

    def getvalue(self):
        return self._buffer.getvalue()

    def truncate(self, size=None):
        current_pos = self._buffer.tell()
        current_size = len(self._buffer.getvalue())
        result = self._buffer.truncate(size)
        if size is not None and size > current_size:
            # Extend with null bytes
            self._buffer.write(b'\x00' * (size - current_size))
            self._buffer.seek(current_pos)  # Restore position
        return result

    @property
    def closed(self):
        return self._closed
