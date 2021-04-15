import logging

# create logger
ena_rec = logging.getLogger(__name__)

class ENArecord(object):
    """
    Class used to encapsulate a single ENA record of a certain type

    Class variables
    ---------------
    type : string
           Record type: i.e. RUN, EXPERIMENT, ...
    primary_id: string
        ENA PRIMARY_ID for this record
    attrbs : dict
             {'TAG' : 'VALUE'}
    xrefs : dict
            {'DB' : 'ID'}
    
    """
    def __init__(self, type, id, attrbs, xrefs):

        ena_rec.debug('Creating an ENArecord object')
        self.type = type
        self.primary_id = id
        self.attrbs = attrbs
        self.xrefs = xrefs

class ENArun(ENArecord):
    """
    Class used to encapsulate an ENA run record

    Class variables
    ---------------
    data_block
    """
    def __init__(self, type, id, attrbs, xrefs, file):
        self.file = file
  
        # invoking the __init__ of the parent class 
        ENArecord.__init__(self, type, id, attrbs, xrefs)

class ENAstudy(ENArecord):
    """
    Class used to encapsulate an ENA study record

    Class variables
    ---------------
    file
    """
    def __init__(self, type, id, attrbs, xrefs, file):
        self.file = file
  
        # invoking the __init__ of the parent class 
        ENArecord.__init__(self, type, id, attrbs, xrefs)

  