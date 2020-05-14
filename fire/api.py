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
    user : str,
           Username for API. Obtained from settings.ini
    """
    def __init__(self, settingsf, pwd):

        api_logger.info('Creating an API object')

        # initialise ConfigParser object with connection
        # settings
        parser = ConfigParser()
        parser.read(settingsf)
        self.settings = parser
        self.user = self.settings.get('fire', 'user')
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

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/blob/" \
                  f"path/{firePath}"

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
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    def fetch_object(self, fireOid=None, firePath=None):
        """
        Function to fetch the metadata associated to a particular
        FIRE object without downloading the archived object

        Parameters
        ----------
        fireOid : str
                  FIRE object id. Optional
        firePath : str
                   FIRE virtual path. Optional

        Returns
        -------
        fire.object.fObject
            Object with metadata
        None if object does not exist in FIRE

        Raises
        ------
        HTTPError
        """

        if fireOid is not None:

            api_logger.info('Fetching FIRE object\'s metadata through its FIRE object id')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/" \
                  f"{fireOid}"
        elif firePath is not None:

            api_logger.info('Fetching FIRE object\'s metadata through its FIRE path')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/path/" \
                  f"{firePath}"

        try:
            res = requests.get(url, auth=(self.user, self.pwd), allow_redirects=True)

            # If the response was successful, no Exception will be raised
            res.raise_for_status()
            json_res = res.json()

            fireObj = None
            fireObj = self.__parse_json_response(json_res)

            api_logger.info('Fetched FIRE object')

            return fireObj

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Error message: {res.text}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            print(f'Error message: {res.text}')

    def __parse_json_response(self, json_res):
        """
        Private function to parse JSON API response
        and will instantiate a fire.object.fObject object

        Parameters
        ----------
        json_res : json response generated
                   by the Requests library

        Returns
        -------
        fire.object
        """

        metadata_dict = {}
        for k, v in json_res.items():
            if k == "filesystemEntry" and v is not None:
                for f in v.keys():
                    metadata_dict[f] = v[f]
            else:
                metadata_dict[k] = v

        fireObj = fObject(**metadata_dict)

        return fireObj


    def push_object(self, fileO, dry=True, publish=True, fire_path=None):
        """
        Function to push (upload) a file.file.File object
        to FIRE

        Parameters
        ----------
        fileO : file.file.File object
                Object to be uploaded
        dry : Bool, optional
              If dry=True then it will not try
              to push the File object to FIRE. Default True
        pubish : Bool, optional
                 If publish=True then the pushed object will
                 be published on upload. Default True
        fire_path : str, optional
                    Virtual path in FIRE to be used for
                    pushing this File.

        Returns
        -------
        fire.object.fObject
                fObject with metadata on the stored FIRE object

        Raises
        ------
        HTTPError
        """

        api_logger.info(f"Pushing File with path: {fileO.name}")

        files = {'file': open(fileO.name, 'rb')}

        url = f"{self.settings.get('fire', 'root_endpoint')}/objects"

        if dry is False:
            try:
                header = {"x-fire-size": f"{fileO.size}",
                          "x-fire-md5": f"{fileO.md5}"}

                if fire_path is not None:
                    api_logger.info(f"Virtual FIRE path provided")
                    header['x-fire-path'] = f"{fire_path}"

                if publish is True:
                    api_logger.info(f"Pushed object will be published")
                    header['x-fire-publish'] = "true"

                res = requests.post(url, auth=(self.user, self.pwd), files=files, headers=header)
                res.raise_for_status()

                if res.status_code == 200:
                    json_res = res.json()
                    fireObj = self.__parse_json_response(json_res)
                    api_logger.info(f"File object pushed with fireOid: {fireObj.fireOid}")

                    return fireObj

            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                print(f'Error message: {res.text}')
            except Exception as err:
                print(f'Other error occurred: {err}')
                print(f'Error message: {res.text}')
        elif dry is True:
            api_logger.info(f"Did not push File with path (dry=True): {fileO.name}")
            api_logger.info(f"Endpoint for pushing is: {url}")
            api_logger.info(f"Use dry=False to effectively push it")

    def update_object(self, attr_name, value, fireOid=None, firePath=None):
        """
        Function to update a certain 'attr_name' of an archived
        FIRE object
        
        Parameters
        ----------
        attr_name : str
                    Attribute name to modify. Required
                    Valid attribute names are: 'firePath'
        value : str
                New value for 'attr_name'. Required
        fireOid : str
                  FIRE object id that will be modified.
                  Optional
        firePath : str
                   FIRE virtual path that will be modified.
                   Optional

        Returns
        -------
        fire.object.fObject with updated 'attr_name'

        Raises
        ------
        HTTPError
        """

        fireObj = None

        if fireOid is not None:
            api_logger.info(f"fireOid provided. Fetching FIRE object that will be modified")
            fireObj = self.fetch_object(fireOid=fireOid)
        elif firePath is not None:
            api_logger.info(f"firePath provided. Fetching FIRE object that will be modified")
            fireObj = self.fetch_object(firePath=firePath)
        elif firePath is None and fireOid is None:
            raise Exception("Either 'firePath' or 'fireOid' need to be "
                            "defined")

        res = None
        if attr_name is 'firePath':
            api_logger.info(f"firePath will be modified")

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/" \
                  f"{fireOid}/firePath"

            header = {"x-fire-path": f"{value}"}

            try:
                res = requests.put(url, auth=(self.user, self.pwd), headers=header)

                res.raise_for_status()
                if res.status_code == 200:
                    json_res = res.json()
                    fireObj = self.__parse_json_response(json_res)

                    api_logger.info(f"Done firePath update")
                    return fireObj

            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                print(f'Error message: {res.text}')
            except Exception as err:
                print(f'Other error occurred: {err}')
                print(f'Error message: {res.text}')



    def delete_object(self, fireOid=None, dry=True):
        """
        Function to delete a certain FIRE object

        Parameters
        ----------
        fireOid : str
                  FIRE object id. Optional
        dry : Bool, optional
              If dry=True then it will not try
              to delete the FIRE object. Default True
        """

        api_logger.info(f"Deleting FIRE object with fireOid: {fireOid}")

        url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/" \
              f"{fireOid}"

        try:
            res = requests.delete(url, auth=(self.user, self.pwd))
            res.raise_for_status()
            api_logger.info(f"FIRE object deleted")

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Error message: {res.text}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            print(f'Error message: {res.text}')