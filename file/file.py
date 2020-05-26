import os
import subprocess
import pdb
import os
import datetime
import logging

# create logger
file_logger = logging.getLogger(__name__)


class File(object):
    """
    Class to represent a File

    Class variables
    ---------------
    file_id : int, Optional,
              Internal DB id if the file is
              stored in the DB
    name : str, Required
           File path
    type : str, Optional
                Type of the file.
                i.e. FASTQ, BAM, CRAM
    host_id : int, Optional
              Host id. Host is the name
              of the host which the
              filesystem is visible
              to so 1000genomes.ebi.ac.uk
              for ebi files. Default : 1
    withdrawn : int, Optional
                1 if self is withdrawn.
                0 otherwise. Default: 0
    md5  : str, Optional
             md5sum of this file
             It will be calculated
             if not defined
    size : int, Optional
           Size in bytes
           It will calculated
           if not defined
    created : str, Optional
              Stringified date representation
              It will calculated if not defined
              in the format (%Y-%m-%d %H:%M:%S)
    """

    def __init__(self, name, host_id=1,
                 withdrawn=0, **kwargs):

        file_logger.debug('Creating File object')

        self.name = name
        self.host_id = host_id
        self.withdrawn = withdrawn

        allowed_keys = ['name', 'type', 'host_id', 'withdrawn', 'file_id',
                        'md5', 'size', 'created', 'updated']

        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        if os.path.isfile(name) == True:
            # path exists, so check if md5sum, size, and created
            # are defined.
            if not hasattr(self, 'md5'):
                self.md5 = self.calc_md5()

            if not hasattr(self, 'size'):
                self.size = os.path.getsize(self.name)

            if not hasattr(self, 'created'):
                self.created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def calc_md5(self):
        """
        Calculate the md5sum of a file

        Returns
        -------
        md5sum string
        """
        command = "md5 -r %s" % self.name

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


