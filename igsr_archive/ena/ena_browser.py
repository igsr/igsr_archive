import logging
import requests
import pdb
import xmltodict

from igsr_archive.config import CONFIG
from igsr_archive.ena.ena_record import ENArun
from requests.exceptions import HTTPError

# create logger
ena_logger = logging.getLogger(__name__)

class ENAbrowser(object):
    """
    Class used to fetch the different records from
    the European Nucleotide Archive (https://www.ebi.ac.uk/ena/browser/home)
    using its REST API

    Class variables
    ---------------
    url : string
          the url used to connect the ENA:
          {CONFIG.get('ena', 'endpoint')}
    """
    def __init__(self):

        ena_logger.debug('Creating an ENA object')
        self.url = f"{CONFIG.get('ena_browser', 'endpoint')}"
    
    def query(self, id):
        """
        Function to query the ENA api

        Parameters
        ----------
        id: string
            ID used to query the API
        
        Returns
        -------
        dict: Dict obtained after parsing the XML returned 
              from requests after parsing with xmltodict() function
        """
        res=None
        try:
            res = requests.get(self.url+f"/{id}")
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Error message: {res.text}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            print(f'Error message: {res.text}')
        else:
            xmld = xmltodict.parse(res.content)
            if res.status_code == 404:
                ena_logger.info('No ENA record found')
            elif res.status_code != 200:
                ena_logger.info('There was an issue in the ENA API request')
                raise Exception(f"Error: {res.text}")
            else:
                ena_logger.debug('Fetched ENA record')
            
            return xmld
    
    def get_run_by_id(self, id):
        """
        Function to get an ENArun object by its ID

        Parameters
        ----------
        id : string
             ENA run id
        
        Returns
        -------
        ENArun object
        """
        xmld = self.query(id)
        id = self.fetch_primary_id('RUN', xmld)
        attrb_dict = self.fetch_attrbs('RUN', xmld)
        xref_dict = self.fetch_xrefs('RUN', xmld)
        file_dict = self.fetch_datablock(xmld)

        ena_run = ENArun(type='RUN', id=id, attrbs=attrb_dict, xrefs=xref_dict, file='a')

        return ena_run

    def get_study_by_id(self, id):
        """
        Function to get an ENAstudy object by its ID

        Parameters
        ----------
        id : string
             ENA study id
        
        Returns
        -------
        ENAstudy object
        """
        pdb.set_trace()
        xmld = self.query(id)
        id = self.fetch_primary_id('STUDY', xmld)
        attrb_dict = self.fetch_attrbs('STUDY', xmld)
        xref_dict = self.fetch_xrefs('STUDY', xmld)

        ena_study = ENArun(type='STUDY', id=id, attrbs=attrb_dict, xrefs=xref_dict, file='a')

        return ena_study


    def fetch_primary_id(self, type, xml_dict):
        """
        Function to fetch the primary_id for this ENA record

        Parameters
        ----------
        type : str
               Type of a certain XML ENA response
               i.e. RUN, EXPERIMENT, and so on ...
        xml_dict : dict 
                   Dict obtained from the ENA response 
                   after parsing with xmltodict function

        Returns
        -------
        str : primary_id
        """
        return xml_dict[f"{type}_SET"][f"{type}"]['IDENTIFIERS']['PRIMARY_ID']

    def guess_type(self, xml_dict):
        """
        Function to guess the type of a certain XML ENA response

        Parameters
        ----------
        xml_dict : dict obtained from the ENA response 
                   after parsing with xmltodict function

        Returns
        -------
        str : type of ENA XML (RUN, EXPERIMENT, STUDY, SAMPLE, ...)
        """

        # guess the type of this record: i.e. RUN, EXPERIMWENT, ...
        valid = [x.strip() for x in CONFIG.get('ena', 'types' ).split(',')]

        type = list(xml_dict.keys())[0].replace('_SET','')
        if type not in valid:
            raise Exception(f"{type} is not valid ENA record type")
        
        return type

    def fetch_datablock(self, xml_dict):
        """
        Function to fetch the <DATA_BLOCK> information

        This is relevant for runs only

        Returns
        -------
        list : list of OrderedDict
        """
        pdb.set_trace()
        files = xml_dict['RUN_SET']['RUN']['DATA_BLOCK']["FILES"]
        
        flist = []
        for k in files.keys():
            fdict = files[k]
            flist.append(fdict)
        
        return flist


    def fetch_attrbs(self, type, xml_dict):
        """
        Function to fetch each of the attributes for this ENA record

        Parameters
        ----------
        type : str
               Type of a certain XML ENA response
               i.e. RUN, EXPERIMENT, and so on ...
        xml_dict : dict 
                   Dict obtained from the ENA response 
                   after parsing with xmltodict function
        
        Returns
        -------
        dict 
             Dictionary in the format {'TAG' : 'VALUE'}
        """
        attrb_lst = xml_dict[f"{type}_SET"][f"{type}"][f"{type}_ATTRIBUTES"][f"{type}_ATTRIBUTE"]

        f_dict = {}
        for item in attrb_lst:
            f_dict[item['TAG']] = item['VALUE']
        
        return f_dict
    
    def fetch_xrefs(self, type, xml_dict):
        """
        Function to fetch each of the xrefs for this ENA record

        Parameters
        ----------
        type : str
               Type of a certain XML ENA response
               i.e. RUN, EXPERIMENT, and so on ...
        xml_dict : dict 
                   Dict obtained from the ENA response 
                   after parsing with xmltodict function
        
        Returns
        -------
        dict 
              Dictionary in the format {'DB' : 'ID'}
        """

        xref_lst = xml_dict[f"{type}_SET"][f"{type}"][f"{type}_LINKS"][f"{type}_LINK"]

        f_dict =  {}
        for item in xref_lst:
            f_dict[item['XREF_LINK']['DB']] = item['XREF_LINK']['ID']
        
        return f_dict