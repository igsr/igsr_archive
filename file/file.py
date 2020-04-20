import os
import subprocess
import pdb

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

    def __init__(self, path, **kwargs):
        self.path = path
        self.__dict__.update(kwargs)

        if not hasattr(self, 'md5sum'):
            self.md5sum = self.calc_md5()

        if not hasattr(self, 'size'):
            self.size = os.path.getsize(self.path)

    def calc_md5(self):
        """
        Calculate the md5sum of a file

        Returns
        -------
        md5sum string
        """
        command = "md5 -r %s" % self.path

        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)

        stdout, stderr = p.communicate()
        md5sum = stdout.decode("utf-8").split(' ')[0].replace('\n', '')
        stderr = stderr.decode("utf-8")

        if stderr:
            print(stderr)

        return md5sum

    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()


