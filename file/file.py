class File(object):
    """
    Class to represent a File

    Class variables
    ---------------
    path : str, Required
           File path
    md5sum : str, Optional
             md5sum of this file
             It will be calculated
             if not defined
    size : int, Optional
           Size in bytes
           It will calculated
           if not defined
    """

    def __init__(self, path, md5sum, size):
        self.path = path
        self.md5sum = md5sum
        self.size = size

