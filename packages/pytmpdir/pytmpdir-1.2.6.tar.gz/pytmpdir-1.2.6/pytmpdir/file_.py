import os
import shutil
import weakref
from datetime import datetime
from datetime import timezone
from pathlib import Path

from .dir_setting import DirSetting
from .pytmpdir_exception import FileClobberError
from .pytmpdir_exception import FileDisappearedError
from .named_temp_file_reader import NamedTempFileReader


class File:
    def __init__(
        self,
        directory: "Directory",
        path: str = "",
        name: str = None,
        pathName: str = None,
        exists: bool = False,
    ):
        """File

        Test whether a path exists.  Set the access and modified time of
        path.  Change the access permissions of a file.

        @param directory: Directory instance.  Default as empty string.
        @param path: File path.
        @param name: File name to be used if passed.
        @param pathName: Joined file name and path to be used if passed.
        @param exists: Passed argument.  Default as False.
        @type directory: Directory
        @type path: String
        @type name: String
        @type pathName: String
        @type exists: Boolean
        """
        # This is for typing
        from .directory_ import Directory

        assert isinstance(
            directory, Directory
        ), "File, directory is not a Directory"
        assert name or pathName, "File, name or pathName"

        self._directoryRef = weakref.ref(directory)

        if name:
            path = path if path else ""
            self._pathName = os.path.join(path, name)

        elif pathName:
            self._pathName = pathName

        self._pathName = self.sanitise(self._pathName)

        if not exists and os.path.exists(self.realPath):
            raise FileClobberError(self.realPath)

        if exists and not os.path.exists(self.realPath):
            raise FileDisappearedError(self.realPath)

        if not os.path.exists(self.realPath):
            with self.open(append=True):
                os.utime(self.realPath, None)
                os.chmod(self.realPath, 0o600)

    @property
    def _directory(self) -> "Directory":
        directory = self._directoryRef()
        from .directory_ import Directory

        assert isinstance(
            directory, Directory
        ), "Directory has been garbage collected"
        return directory

    # ----- Name and Path setters
    @property
    def path(self) -> str:
        """Path

        Determines directory name.

        @return: Path as string.
        """

        return os.path.dirname(self.pathName)

    @path.setter
    def path(self, path: str):
        """Path Setter

        Set path with passed in variable.

        @param path: New path string.
        @type path: String
        """
        path = str(Path(path)) if path else ""
        self.pathName = os.path.join(path, self.name)

    @property
    def name(self) -> str:
        """Name

        Determines working directory.

        @return: Directory name as string.
        """

        return os.path.basename(self.pathName)

    @name.setter
    def name(self, name: str):
        """Name Setter

        Set name with passed in variable.

        @param name: New name string.
        @type name: String
        """

        self.pathName = os.path.join(self.path, name)

    @property
    def pathName(self) -> str:
        """Path Name

        Returns stored path name.

        @return: Path Name as string.
        """

        return self._pathName

    @pathName.setter
    def pathName(self, pathName: str):
        """Path Name Setter

        Set path name with passed in variable, create new directory and move
        previous directory contents to new path name.

        @param pathName: New path name string.
        @type pathName: String
        """

        if self.pathName == pathName:
            return

        pathName = self.sanitise(pathName)
        before = self.realPath
        after = self._realPath(pathName)

        assert not os.path.exists(after), "File after doesn't exist"

        newRealDir = os.path.dirname(after)
        if not os.path.exists(newRealDir):
            os.makedirs(newRealDir, DirSetting.defaultDirChmod)

        shutil.move(before, after)

        oldPathName = self._pathName
        self._pathName = pathName

        self._directory._fileMoved(oldPathName, self)

    def open(self, append=False, write=False, asBin=True):
        """Open

        Return a file-object for opening this file.

        :param append: Open the file for appending to the end of the file if
            it exists.  Default as False.
        :param write: Open the file for overwriting
        :param asBin: Open the file as binary.
        """
        assert not isinstance(append, str), (
            "Append was not True or False, got %s" % append
        )

        flag = {
            (False, False): "r",
            (True, False): "a",
            (True, True): "a",
            (False, True): "w",
        }[(append, write)]

        if asBin:
            flag += "b"

        realPath = self.realPath
        realDir = os.path.dirname(realPath)
        if not os.path.exists(realDir):
            os.makedirs(realDir, DirSetting.defaultDirChmod)
        return open(self.realPath, flag)

    def namedTempFileReader(self) -> NamedTempFileReader:
        """Named Temporary File Reader

        This provides an object compatible with NamedTemporaryFile, used for reading this
        files contents. This will still delete after the object falls out of scope.

        This solves the problem on windows where a NamedTemporaryFile can not be read
        while it's being written to
        """

        return NamedTempFileReader(self._directory, self)

    def delete(self):
        """Delete

        Deletes directory and drops the file name from dictionary.  File on
        file system removed on disk.
        """

        realPath = self.realPath
        assert os.path.exists(realPath), "File.delete, realPath doesn't exist"
        os.remove(realPath)

        self._directory._fileDeleted(self)

    def remove(self):
        """Remove

        Removes the file from the Directory object, file on file system
        remains on disk.
        """
        self._directory._fileDeleted(self)

    @property
    def size(self) -> int:
        """Size

        Determines size of directory.

        @return: Total size, in bytes.
        """

        return os.stat(self.realPath).st_size

    @property
    def mTime(self) -> datetime:
        """mTime

        Return the last modification time of a file, reported by os.stat().

        @return: Time as string.
        """

        return datetime.fromtimestamp(
            os.path.getmtime(self.realPath), tz=timezone.utc
        )

    @property
    def isContentAscii(self):
        with self.open(asBin=True) as f:
            data = f.read(40000)
            try:
                data.decode("ascii")
                return True
            except UnicodeDecodeError:
                return False

    isContentText = isContentAscii

    @property
    def realPath(self) -> str:
        """Real Path

        Get path name.

        @return: Path Name as string.
        """
        return self._realPath()

    def _realPath(self, newPathName: str = None) -> str:
        """Private Real Path

        Get path name.

        @param newPathName: variable for new path name if passed argument.
        @type newPathName: String
        @return: Path Name as string.
        """
        return os.path.join(
            self._directory.path, newPathName if newPathName else self._pathName
        )

    def sanitise(self, pathName: str) -> str:
        """Sanitise

        Clean unwanted characters from the pathName string.

        @param pathName: Path name variable.
        @type pathName: String
        @return: Path name as string.
        """
        assert isinstance(pathName, str), "sanitise, pathName not a str"
        assert not pathName.endswith(os.sep), "pathName ends with %s" % os.sep

        pathName = str(Path(os.path.normpath(pathName)))

        while pathName.startswith(os.sep):
            pathName = pathName[1:]

        assert not pathName.startswith(".."), f"{pathName} starts with '..' "
        assert "/.." not in pathName, f"{pathName} contains '/..' "

        return pathName
