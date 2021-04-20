import logging
import pdb

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
        allowed_keys = {'attrbs', 'xrefs','fastq_ftp', 
                        'fastq_bytes', 'fastq_md5', 
                        'submitted_ftp', 'submitted_bytes',
                        'submitted_md5', 'sra_ftp', 'sra_bytes', 'sra_md5'}
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
        tuple : tuple of ENArecords
        """
        pdb.set_trace()
        for attr in fields:
            value = getattr(self, attr, None)        
            if value is None:
                raise Exception(f"Attribute {attr} could not be found in the ENArecord instance")

        print("h")


    
    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()
        