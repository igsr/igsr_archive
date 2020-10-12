import logging
import re
import pdb
import sys
import json
from subprocess import Popen, PIPE
from configparser import ConfigParser
from igsr_archive.utils import is_tool

import requests
from requests.exceptions import HTTPError
from igsr_archive.object import fObject

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

        api_logger.debug('Creating an API object')

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

            api_logger.debug('Retrieving a FIRE object through its FIRE object id')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/blob/" \
                  f"{fireOid}"
        elif firePath is not None:

            api_logger.debug('Retrieving a FIRE object through its FIRE path')

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

            api_logger.debug('Retrieved object')

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

            api_logger.debug('Fetching FIRE object\'s metadata through its FIRE object id')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/" \
                  f"{fireOid}"
        elif firePath is not None:

            api_logger.debug('Fetching FIRE object\'s metadata through its FIRE path')

            url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/path/" \
                  f"{firePath}"
        else:
            print("Could not fetch the object. Please provide either a fireOid or a firePath")
            sys.exit(1)

        res = None
        try:
            res = requests.get(url, auth=(self.user, self.pwd), allow_redirects=True)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Error message: {res.text}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            print(f'Error message: {res.text}')
        else:
            json_res = res.json()

            fireObj = None
            if res.status_code == 404:
                api_logger.info('No FIRE object found')
                return fireObj
            else:
                fireObj = self.__parse_json_response(json_res)
                api_logger.info('Fetched FIRE object')
                return fireObj

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
        to FIRE. This function currently uses 'curl'.
        As the standars 'requests' module throws memory errors
        when trying to upload large files

        Parameters
        ----------
        fileO : file.file.File object
                Object to be uploaded
        dry : Bool, optional
              If dry=True then it will not try
              to push the File object to FIRE. Default True
        publish : Bool, optional
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

        if is_tool("curl") is False:
            raise Exception("The 'curl' program was not found in this system. Can't continue!...")

        url = f"curl {self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects" \
              f" -u {self.user}:{self.pwd}"

        fire_obj = None
        if dry is False:
            # FIRE api requires atomic operations, so the POST request must be atomic
            # and also multiple atomic PUSH requests for providing fire path and publishing
            url = url+f" -F file=@{fileO.name} -H 'x-fire-md5: {fileO.md5}' -H 'x-fire-size: {fileO.size}' "
            p = Popen(url, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = p.communicate()
            res = stdout.decode("utf-8")

            fire_obj = None
            api_logger.debug(f"API response:{res}")
            # FIRE api is down
            if res == "Service Unavailable":
                raise HTTPError("FIRE Service Unavailable")
            d = json.loads(stdout)
            if "statusCode" in d.keys():
                err = f"{d['statusMessage']}\n{d['detail']}"
                raise HTTPError(err)
            else:
                fire_obj = self.__parse_json_response(d)
                api_logger.info(f"File object pushed with fireOid: {fire_obj.fireOid}")

            if fire_path is not None:
                api_logger.info(f"Virtual FIRE path provided")
                fire_obj = self.update_object(attr_name='firePath', value=fire_path,
                                              fireOid=fire_obj.fireOid, dry=False)
                assert fire_obj is not None, "Error adding a FIRE path to the object"
            if publish is True:
                api_logger.info(f"Pushed object will be published")
                fire_obj = self.update_object(attr_name='publish', value=True,
                                              fireOid=fire_obj.fireOid, dry=False)
                assert fire_obj is not None, "Error adding a publishing the object"

            return fire_obj
        elif dry is True:
            api_logger.info(f"Did not push File with path (dry=True): {fileO.name}")
            api_logger.info(f"Endpoint for pushing is: {url}")
            api_logger.info(f"Use --dry False to effectively push it")

    def update_object(self, attr_name, value, dry=True, fireOid=None, firePath=None):
        """
        Function to update a certain 'attr_name' of an archived
        FIRE object
        
        Parameters
        ----------
        attr_name : str
                    Attribute name to modify. Required
                    Valid attribute names are: 'firePath', 'publish'
        value : str
                New value for 'attr_name'. Required
        dry : Bool, optional
              If dry=True then it will not try
              to update the archived FIRE object. Default True
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
        header = None
        url = f"{self.settings.get('fire', 'root_endpoint')}/{self.settings.get('fire', 'version')}/objects/" \
              f"{fireOid}/"
        if attr_name is 'firePath':
            api_logger.info(f"firePath will be modified")
            url = url + "firePath"
            header = {"x-fire-path": f"{value}"}
        elif attr_name is 'publish':
            api_logger.info(f"publish will be set to {value} for this FIRE object")
            url = url + "publish"

        if dry is False:
            try:
                if header is not None:
                    res = requests.put(url, auth=(self.user, self.pwd), headers=header)
                else:
                    if value is True:
                        # 'publish' will be set to True
                        res = requests.put(url, auth=(self.user, self.pwd))
                    elif value is False:
                        # 'publish' will be set to False
                        res = requests.delete(url, auth=(self.user, self.pwd))
                res.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                print(f'Error message: {res.text}')
            except Exception as err:
                print(f'Other error occurred: {err}')
                print(f'Error message: {res.text}')
            else:
                if res.status_code == 200:
                    json_res = res.json()
                    fireObj = self.__parse_json_response(json_res)
                    api_logger.info(f"Done FIRE object update")
                    return fireObj
        elif dry is True:
            api_logger.info(f"FIRE object with fireOid: {fireOid} is going to be updated")
            api_logger.info(f"FIRE object attribute {attr_name} is going to be updated with value {value}")
            api_logger.info(f"FIRE object was not updated")
            api_logger.info(f"Use --dry False to update it")
        else:
            raise Exception(f"dry option: {dry} not recognized")

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

        if dry is False:
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
        elif dry is True:
            api_logger.info(f"FIRE object with fireOid: {fireOid} is going to be deleted")
            api_logger.info(f"FIRE object was not deleted")
            api_logger.info(f"Use --dry False to deleted it")
        else:
            raise Exception(f"dry option: {dry} not recognized")
