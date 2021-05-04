import logging

# create logger
ix_logger = logging.getLogger(__name__)

class Index(object):
    """
    Class to represent an Index of the metadata information
    on objects archived in the European Nucleotide Archive
    (ENA)

    Class variables
    ---------------
    """
    def __init__(self):

        ix_logger.debug('Creating Index object')
