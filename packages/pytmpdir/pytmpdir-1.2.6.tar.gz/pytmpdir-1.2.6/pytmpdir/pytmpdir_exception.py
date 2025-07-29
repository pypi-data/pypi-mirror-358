class FileDisappearedError(Exception):
    """File Disappeared Error

    Raise Exception if file does not exist .
    """

    pass


class FileClobberError(Exception):
    """File Clobber Error

    Raise Exception if path does not exist.
    """

    pass
