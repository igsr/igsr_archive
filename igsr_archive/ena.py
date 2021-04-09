import logging

from igsr_archive.config import CONFIG


# create logger
ena_logger = logging.getLogger(__name__)

class ENA(object):
    """
    Class used to fetch the different records from
    the European Nucleotide Archive (https://www.ebi.ac.uk/ena/browser/home)
    using its rest API

    Class variables
    ---------------
    """
    def __init__(self, pwd):

        ena_logger.debug('Creating an ENA object')