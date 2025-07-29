import os.path
from tempfile import NamedTemporaryFile


class DirSetting:
    """Directory Settings

    User configuration settings.
    """

    tmpDirPath = os.path.dirname(NamedTemporaryFile().name)
    defaultDirChmod = 0o700
