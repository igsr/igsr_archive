import logging
import pdb
import inspect

from igsr_archive.config import CONFIG

# create logger
ena_rec = logging.getLogger(__name__)

class ENArecord(object):
    """
    Class used to encapsulate a single ENA record of a certain type

    Class variables
    ---------------
    type : string, required
           Record type: i.e. RUN, EXPERIMENT, ...
    accession: string, required
        ENA accession for this record
    attrbs : dict, optional
             {'TAG' : 'VALUE'}
    xrefs : dict, optional
            {'DB' : 'ID'}
    """
    def __init__(self, type, id, **kwargs):

        ena_rec.debug('Creating an ENArecord object')
       
        self.type = type
        self.accession = id
        allowed_keys_str = CONFIG.get('ena', 'fields').replace('\n', '')
        allowed_keys = set(allowed_keys_str.split(","))
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

    def split(self, fields = ['fastq_ftp', 'fastq_bytes', 'fastq_md5']):
        """
        Function to split the record having more than one piece 
        of information per field: i.e. ('ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_1.fastq.gz;ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_2.fastq.gz')
        into 2 ENA records

        Parameters
        ----------
        fields : list
                 Fields that will be splitted. Default: ['fastq_ftp', 'fastq_bytes', 'fastq_md5']

        Returns
        -------
        list : list of ENArecord objects
        """
        n = len(self.__getattribute__(fields[0]).split(";"))
        list_d = [{} for _ in range(n)]
        
        # get all attributes from self
        for i in inspect.getmembers(self):
            # to remove private and protected
            # functions
            if not i[0].startswith('_'):
                # To remove other methods that
                # doesnot start with a underscore
                if not inspect.ismethod(i[1]) and not i[0]=='type' and not i[0]=='accession':
                    if i[0] in fields:
                        bits = i[1].split(";")
                        ix = 0
                        for data in list_d:
                            data[i[0]] = bits[ix]
                            ix += 1
                    else:
                        for data in list_d:
                            data[i[0]] = i[1]

        lst_objs = [ENArecord(type=self.type, id=self.accession, **adict) for adict in list_d]
        return lst_objs
    
    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()
        