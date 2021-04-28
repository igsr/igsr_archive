import logging
import requests
import pdb
import xmltodict

from igsr_archive.config import CONFIG
from igsr_archive.ena.ena_record import ENArecord
from requests.exceptions import HTTPError

# create logger
ena_logger = logging.getLogger(__name__)
class ENA(object):
    """
    Super class representing a connection to the ENA (https://www.ebi.ac.uk/ena/) API
    
    Class variables
    ---------------
    url : string 
          URL used for the query
    """
    def __init__(self, url):
        """
        Constructor
        -----------
        url : string 
              URL used in the query function
        """
        ena_logger.debug('Creating an ENAquery object')
        self.url = url

    def query(self):
        """
        Function to query the ENA api
        
        Returns
        -------
        res : requests.models.Response
        """
        res=None
        try:
            res = requests.get(self.url)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Error message: {res.text}')
        except Exception as err:
            print(f'Other error occurred: {err}')
            print(f'Error message: {res.text}')
        else:
            if res.status_code == 404:
                ena_logger.info('No ENA record found')
            elif res.status_code != 200:
                ena_logger.info('There was an issue in the ENA API request')
                raise Exception(f"Error: {res.text}")
            else:
                ena_logger.debug('Query was successful')
                return res

class ENAbrowser(ENA):
    """
    Class used to fetch the different records from
    the European Nucleotide Archive (https://www.ebi.ac.uk/ena/browser/home)
    using its REST API
    """
    def __init__(self, acc):
        """
        Constructor
        -----------
        acc: string
              accession to query the API
        """
        ena_logger.debug('Creating an ENAbrowser object')
        
        url = f"{CONFIG.get('ena', 'endpoint_browser')}/{acc}"

        ENA.__init__(self, url)
    
    def query(self):
        """
        Function overriding 'query' parent class

        Returns
        ------
        dict : containing the result of converting the XML response
               to dict
        """
        res = ENA.query(self)
        return xmltodict.parse(res.content)
    
    def get_record(self, xmld):
        """
        Function to get a ENArecord object

        Parameters
        ----------
        xmld : dict
               containing the result of converting the XML response
               to dict
        
        Returns
        -------
        ENArecord object
        """
        type = self.guess_type(xmld)
        id = self.fetch_primary_id(type, xmld)
        attrb_dict = self.fetch_attrbs(type, xmld)
        xref_dict = self.fetch_xrefs(type, xmld)

        ena_record = ENArecord(type=type, id=id, attrbs=attrb_dict, xrefs=xref_dict)

        return ena_record

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
        files = xml_dict['RUN_SET']['RUN']['DATA_BLOCK']["FILES"]
        
        flist = []
        for k in files.keys():
            fdict = files[k]
            flist.append(fdict)
        
        return flist

    def fetch_attrbs(self, type, xml_dict, alist=None):
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
        alist : list
                Return only the attributes specified by
                this argument
        
        Returns
        -------
        dict 
             Dictionary in the format {'TAG' : 'VALUE'}
        """
        attrb_lst = xml_dict[f"{type}_SET"][f"{type}"][f"{type}_ATTRIBUTES"][f"{type}_ATTRIBUTE"]

        f_dict = {}
        for item in attrb_lst:
            if alist is not None:
                if item['TAG'] not in alist:
                    continue
            if 'VALUE' in item:
                f_dict[item['TAG']] = item['VALUE']
            else:
                f_dict[item['TAG']] = None

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
        if isinstance(xref_lst, list):
            for item in xref_lst:
                f_dict[item['XREF_LINK']['DB']] = item['XREF_LINK']['ID']
        else:
            f_dict[xref_lst['XREF_LINK']['DB']] = xref_lst['XREF_LINK']['ID']
                
        return f_dict

class ENAportal(ENA):
    """
    Class used to fetch the different filereports from
    the European Nucleotide Archive (https://www.ebi.ac.uk/ena/portal/home)
    using its filereport REST API

    Class variables
    ---------------
    url : string
          the url used to connect the ENA:
          {CONFIG.get('ena', 'endpoint_portal')}
    """
    def __init__(self, acc):
        """
        Constructor
        -----------
        acc: string
             accession to query the API
        """

        ena_logger.debug('Creating an ENAportal object')
        url = f"{CONFIG.get('ena', 'endpoint_portal')}{acc}"

        ENA.__init__(self, url)

    def query(self, q_type='read_run', fields=None):
        """
        Function overriding 'query' parent class

        Parameters
        ----------
        q_type : str
               Report type: 'read_run', 'analysis'
               Default: 'read_run'
        fields : str
                 comma-sep string with fields to fetch
                 in this filereport. Default : none

        Returns
        -------
        list : List with ENArecord objects
        """
        if q_type != 'read_run' and q_type != 'analysis':
            raise TypeError(f"Non valid 'q_type' parameter:{q_type}")

        if fields is None:
            self.url = f"{self.url}&result={q_type}"
        else :
            self.url = f"{self.url}&result={q_type}&fields={fields}"
        res = ENA.query(self)

        text_res = res.content.decode("utf-8")
        data = [x.split('\t') for x in text_res.split('\n') if len(x.split('\t'))>1]
        fields = data[0]
        # getting the 'type' of this file record
        type = None
        if q_type == 'read_run':
            type = fields[0].replace('_accession','').upper()
        else:
            type = 'ANALYSIS'
        
        data = data[1::]

        records = []
        for rec in data:
            record = {}
            if len(rec) != len(fields):
                raise Exception("Different number of data columns and fields")
            record = dict(zip(fields, rec))
            if q_type == 'read_run':
                records.append(ENArecord(type, record['run_accession'], **record))
            elif q_type == "analysis":
                records.append(ENArecord(type, record['analysis_accession'], **record))

        return records