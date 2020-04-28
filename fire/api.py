import logging
import requests
import pdb
import re

from requests.exceptions import HTTPError
from configparser import ConfigParser
from fire.object import fObject

# create logger
api_logger = logging.getLogger(__name__)


class API(object):
    """
    Class to deal with the queries to the FIRE API for
    archival and retrieval activities

    Class variables
    ---------------
    settingsf : str, Required
               Path to *.ini file with MySQL server connection settings
    pwd : str, Required
          Password for API
    user : str, Required
           Username for API
    """
    def __init__(self, settingsf, user, pwd):

        api_logger.info('Creating an API object')

        # initialise ConfigParser object with connection
        # settings
        parser = ConfigParser()
        parser.read(settingsf)
        self.settings = parser
        self.user = user
        self.pwd = pwd

    def get_filename_from_cd(self, cd):
        """
        Get filename from content-disposition

        Parameters
        ----------
        cd : str
             Content disposition from Requests.headers
        """
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        return fname[0]

    def retrieve_object(self, fireOid=None, firePath=None, outfile=None):
        """
        Function to retrieve (download) a particular FIRE object

        Parameters
        ----------
        fireOid : str
                  FIRE object id. Optional
        firePath : str
                   FIRE path id. Optional
        outfile : file
                  Output file name. Optional.

        Returns
        -------
        file : Downloaded file

        Raises
        ------
        HTTPError
        """

        # construct url
        if fireOid is not None:

            api_logger.info('Retrieving a FIRE object through its FIRE object id')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/blob/" \
                  f"{fireOid}"
        elif firePath is not None:

            api_logger.info('Retrieving a FIRE object through its FIRE path')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/path/" \
                  f"{firePath}"

        try:
            r = requests.get(url, auth=(self.user, self.pwd), allow_redirects=True)
            if outfile is None:
                # if outfile is not provided then it will not change the original filename
                # and will place the file in workdir
                outfile = self.get_filename_from_cd(r.headers.get('content-disposition'))

            open(outfile, 'wb').write(r.content)

            # If the response was successful, no Exception will be raised
            r.raise_for_status()

            api_logger.info('Retrieved object')

            return outfile
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6

    def fetch_object(self, fireOid=None):
        """
        Function to fetch the metadata associated to a particular
        FIRE object

        Parameters
        ----------
        fireOid : str
                  FIRE object id. Optional

        Returns
        -------
        fire.object.fObject
            Object with metadata

        Raises
        ------
        HTTPError
        """

        if fireOid is not None:

            api_logger.info('Fetching FIRE object\'s metadata through its FIRE object id')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/" \
                  f"{fireOid}"

        try:
            r = requests.get(url, auth=(self.user, self.pwd), allow_redirects=True)

            # If the response was successful, no Exception will be raised
            r.raise_for_status()

            json_res = r.json()

            metadata_dict = {}
            for k, v in json_res.items():
                if k == "filesystemEntry":
                    for f in v.keys():
                        metadata_dict[f] = v[f]
                else:
                    metadata_dict[k] = v

            fireObj = fObject(**metadata_dict)

            api_logger.info('Created fire.object.Object')

            return fireObj

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
