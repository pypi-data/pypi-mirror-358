# Created by Synerty Pty Ltd
# Copyright (C) 2013-2017 Synerty Pty Ltd (Australia)
#
# This software is open source, the MIT license applies.
#
# Website : http://www.synerty.com
# Support : support@synerty.com

import os
import shutil
import tempfile
import weakref
from pathlib import Path
from platform import system
from subprocess import check_output
import logging
from .dir_setting import DirSetting
from .file_ import File

logger = logging.getLogger(__name__)

_isWindows = system() == "Windows"
_isMacOS = system() == "Darwin"


textChars = bytearray([7, 8, 9, 10, 12, 13, 27]) + bytearray(
    list(range(0x20, 0x100))
)


def is_binary_string(data):
    """Is Binary String

    Determines if the input variable contains specific ASCII
    characters.

    @param data: Input variable being checked if it's a string.
    @return: True if variable is string.
    """

    return bool(data.translate(None, textChars))


class Directory:
    """Directory

    Functions as a directory object to extract, archive and pass around code.
    Auto deletes when the directory falls out of scope.
    """

    def __init__(
        self,
        initWithDir: str = None,
        autoDelete: bool = True,
        inDir: str = None,
    ):
        """Directory Initialise

        Creates a temporary directory if the directory doesn't exist.

        :param initWithDir: Create based on an existing directory
        :param autoDelete: Remove temporary files and folders. Default as True.
        :param inDir: Create a new temporary directory under this directory.
        """
        self._files = {}
        self._autoDelete = autoDelete

        if initWithDir:
            self._path = str(initWithDir)
            self.scan()

        else:
            if (
                os.path.isdir(inDir if inDir else DirSetting.tmpDirPath)
                is False
            ):
                os.mkdir(inDir if inDir else DirSetting.tmpDirPath)
            self._path = tempfile.mkdtemp(
                dir=(inDir if inDir else DirSetting.tmpDirPath)
            )

            closurePath = self._path

        def cleanup(me):
            """Cleanup

            Recursively delete a directory tree of the created path.
            """

            if autoDelete:
                shutil.rmtree(closurePath)

        self.__cleanupRef = weakref.ref(self, cleanup)

    @property
    def path(self) -> str:
        """Path

        :return The absolute path of this directory
        """
        return self._path

    @property
    def delete(self) -> bool:
        """Delete

        :return True if this directory will delete it's self when it falls out of scope.
        """
        return self._autoDelete

    @property
    def files(self) -> [File]:
        """Files

        @return: A list of the Directory.File objects.
        """
        return list(self._files.values())

    @property
    def pathNames(self) -> [str]:
        """Path Names

        @return: A list of path + name of each file, relative to the root
        directory.
        """

        return [f.pathName for f in list(self._files.values())]

    @property
    def paths(self) -> list[str]:
        """Paths

        @return: A list of the paths, effectively a list of relative
        directory names.
        """

        return list(set([f.path for f in list(self._files.values())]))

    def getFile(
        self, path: str = "", name: str = None, pathName: str = None
    ) -> File:
        """Get File

        Get File name corresponding to a path name.

        @param path: File path.  Default as empty string.
        @param name: File name to be used if passed.
        @param pathName: Joined file name and path to be used if passed.
        @type path: String
        @type name: String
        @type pathName: String
        @return: Specific file from dictionary.
        """

        assert name or pathName, "Directory.getFile, name or pathName"

        if _isWindows:
            path = str(Path(path)) if path else path
            pathName = str(Path(pathName)) if pathName else pathName

        pathName = pathName if pathName else os.path.join(path, name)
        return self._files.get(pathName)

    def createFile(
        self, path: str = "", name: str = None, pathName: str = None
    ) -> File:
        """Create File

        Creates a new file and updates file dictionary.

        @param path: File path.  Defaults as empty string.
        @param name: File name to be used if passed.
        @param pathName: Joined file name and path to be used if passed.
        @type path: String
        @type name: String
        @type pathName: String
        @return: Created file.
        """
        if _isWindows:
            path = str(Path(path)) if path else path
            pathName = str(Path(pathName)) if pathName else pathName

        file = File(self, path=path, name=name, pathName=pathName)
        self._files[file.pathName] = file
        return file

    def createTempFile(self, suffix=None, prefix=None, secure=True) -> File:
        """Create File

        Creates a new file within the directory with a temporary file like name.

        @return: Created file.
        """
        if not secure:
            raise NotImplementedError(
                "We only support secure files at this point"
            )

        # tempfile.mkstemp(suffix=None, prefix=None, dir=None, text=False)

        newFileNum, newFileRealPath = tempfile.mkstemp(
            suffix=suffix, prefix=prefix, dir=self._path
        )
        os.close(newFileNum)

        relativePath = os.path.relpath(newFileRealPath, self.path)

        file = File(self, pathName=relativePath, exists=True)
        self._files[file.pathName] = file
        return file

    def createHiddenFolder(self) -> File:
        """Create Hidden Folder

        Create a hidden folder.  Raise exception if auto delete isn't True.

        @return: Created folder.
        """
        if not self._autoDelete:
            raise Exception(
                "Hidden folders can only be created within"
                " an autoDelete directory"
            )
        return tempfile.mkdtemp(dir=self.path, prefix=".")

    def _listFilesPy(self) -> [File]:
        """List Files for Windows OS

        Search and list the files and folder in the current directory for the
        Windows file system.

        @return: List of directory files and folders.
        """

        output = []
        for dirname, dirnames, filenames in os.walk(self._path):
            for filename in filenames:
                output.append(os.path.join(dirname, filename))
        return output

    def _listFilesPosix(self) -> [File]:
        """List Files for POSIX

        Search and list the files and folder in the current directory for the
        POSIX file system.

        @return: List of directory files and folders.
        """

        find = "find %s -type f" % self._path
        output = check_output(args=find.split()).strip().decode().split("\n")
        return output

    def scan(self) -> [File]:
        """Scan

        Scan the directory for files and folders and update the file dictionary.

        @return: List of files
        """

        self._files = {}
        # macOS sandboxes don't support running find.
        output = (
            self._listFilesPy()
            if _isWindows or _isMacOS
            else self._listFilesPosix()
        )
        output = [line for line in output if "__MACOSX" not in line]
        for pathName in output:
            if not pathName:  # Sometimes we get empty lines
                continue

            pathName = pathName[len(self._path) + 1 :]
            file = File(self, pathName=pathName, exists=True)
            self._files[file.pathName] = file

        return self.files

    def clone(self, autoDelete: bool = True) -> "Directory":
        """Clone

        Recursively copy a directory tree.  Removes the destination
        directory as the destination directory must not already exist.

        @param autoDelete: Used to clean up files on completion.  Default as
        True.
        @type autoDelete: Boolean
        @return: The cloned directory.
        """
        d = Directory(autoDelete=autoDelete)
        os.rmdir(d.path)  # shutil doesn't like it existing
        shutil.copytree(self.path, d.path)
        d.scan()
        return d

    def _fileDeleted(self, file: File):
        """File Deleted

        Drop the file name from dictionary.

        @param file: File name.
        @type file: File
        """
        self._files.pop(file.pathName)

    def _fileMoved(self, oldPathName: str, file: File):
        """File Moved

        Drop the old file name from the dictionary and add the new file name.

        @param oldPathName: Previous dictionary path name.
        @param file: File name.
        @type oldPathName: String
        @type file: File
        """
        self._files.pop(oldPathName)
        self._files[file.pathName] = file
