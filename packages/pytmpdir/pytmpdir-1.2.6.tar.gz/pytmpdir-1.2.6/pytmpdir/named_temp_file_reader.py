import weakref


class _NamedTempFileReaderCloser:
    def __init__(self, fileObject):
        self._isClosed = False
        self._fileObject = fileObject

    def close(self, *args):
        if self._isClosed:
            return
        self._fileObject.close()
        self._isClosed = True


class NamedTempFileReader:
    """Named Temp File

    This pytmpdir version of the NamedTemporaryFile keeps a strong reference to the
    C{Directory} object, meaning you can pass it around just like a NamedTemporaryFile
    and it will delete when it's done.

    ::

        dir = Directory()
        file = dir.createTempFile()

        # Write the data to the file, this closes it properly, allowing the reader to read
        with file.open(write=True) as f:
            f.write("some thing")

        namedTempReader = file.namedTempFileReader()

        # Pass namedTempReader to other code that takes a NamedTemporaryFile
        somthingElse(namedTempReader)

    """

    def __init__(self, directory: "Directory", file: "File"):
        self._directory = directory
        self._file = file
        self._fileObject = self._file.open()

        self._closer = _NamedTempFileReaderCloser(self._fileObject)
        self.__cleanupRef = weakref.ref(self, self._closer.close)

    @property
    def name(self) -> str:
        """Delete

        :return The abolote path and file name of this file.
        """
        return self._file.realPath

    @property
    def delete(self) -> bool:
        """Delete

        :return True if the file will be deleted when all references to the directory
                    including this objects reference, fall out of scope.
        """
        return self._directory.delete

    @delete.setter
    def delete(self, value: bool):
        raise Exception("You can not turn off auto delete for this class")

    def close(self):
        """Close

        Closes the underlying file object
        """
        self._closer.close()

    def __enter__(self):
        self._fileObject.__enter__()
        return self

    def __exit__(self, exc, value, tb):
        result = self._fileObject.__exit__(exc, value, tb)
        self.close()
        return result

    def __iter__(self):
        for line in self._fileObject:
            yield line
