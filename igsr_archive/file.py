import subprocess
import os
import pdb
import datetime
import logging
from igsr_archive.utils import is_tool
from igsr_archive.config import CONFIG

# create logger
file_logger = logging.getLogger(__name__)

class File(object):
    """
    Class to represent a File

    Attributes
    ----------
    name : str
           File path.
    file_id : int
              Internal DB id if the file is
              stored in the DB.
    type : str
           Type of the file.
           i.e. FASTQ, BAM, CRAM.
    host_id : int
              Host id. Host is the name of the host which the
              filesystem is visible to 1000genomes.ebi.ac.uk
              for ebi files.
    withdrawn : int
                1 if self is withdrawn.
                0 otherwise.
    md5  : str
            md5sum of this filenIt will be calculated if not defined.
    size : int
           Size in bytes. It will calculated
           if not defined.
    created : str
              Stringified date representation
              It will be calculated if not defined in the format (%Y-%m-%d %H:%M:%S).
    """

    def __init__(self, name, host_id=1, type=None,
                 withdrawn=0, **kwargs):
        """
        Constructor

        Parameters
        ----------
        name : str
               File path.
        host_id: int, default=1
                 Host id. Host is the name of the host which the filesystem is visible to 
                 1000genomes.ebi.ac.uk for ebi files.
        type : str, default=None
               Type of the file. i.e. FASTQ, BAM, CRAM.
        withdrawn : int, default=0
                    1 if self is withdrawn.
                    0 otherwise.
        **kwargs : dict, optional
                   Extra arguments to `File`: refer to each File documentation for a
                   list of all possible arguments.
        """

        file_logger.debug('Creating File object')

        self.name = name
        self.host_id = host_id
        self.type = type
        self.withdrawn = withdrawn

        allowed_keys = ['name', 'type', 'host_id', 'withdrawn', 'file_id',
                        'md5', 'size', 'created', 'updated']

        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

        if os.path.isfile(name):

            file_logger.debug(f"Found a file with name: {name}")

            # Mutate name to absolute path
            self.name =os.path.abspath(name)
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
        md5sum : str
                 md5sum of `self`.
        
        Raises
        ------
        Exception
        """
        file_logger.info(f"Calculating md5 checksum with file: {self.name}")

        # check if either md5 or md5sum are installed
        # and adjust md5 the command
        command = None
        if is_tool('md5'):
            command = "md5 -r %s" % self.name
        elif is_tool('md5sum'):
            command = f"md5sum {self.name}"

        if command is None:
            raise Exception("No executable for calculating the md5 checksum was found. Do you have md5 or md5sum"
                            "on your PATH?")

        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)

        stdout, stderr = p.communicate()
        md5sum = stdout.decode("utf-8").split(' ')[0].replace('\n', '')
        stderr = stderr.decode("utf-8")

        if stderr:
            print(stderr)

        file_logger.info(f"Done")

        return md5sum

    def guess_type(self):
        """
        Function to get the type of a file depending on the
        'file_type_rules' section of CONFIG
        
        Returns
        -------
        str : type of file
        """
        assert CONFIG.has_section('file_type_rules') is True, "Provide a 'file_type_rules' section in your *.ini file"

        rules_dict = CONFIG._sections['file_type_rules']

        ext = None
        ext = os.path.basename(self.name).split('.')[-1]
        assert ext is not None, f"*.ext could not be obtained from {self.name}"

        if ext not in rules_dict:
            # assign the default file type
            return rules_dict['default']
        else:
            return rules_dict[ext]

    def check_if_exists(self):
        """
        Function to check if a file with self.name
        (absolute or relative) exists

        Returns
        -------
        bool
             True if file exists. False otherwise.
        """
        return os.path.isfile(self.name)

    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()
