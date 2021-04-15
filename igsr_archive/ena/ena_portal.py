import logging

from igsr_archive.config import CONFIG

# create logger
enaportal_logger = logging.getLogger(__name__)


class ENAportal(object):
    """
    Class used to fetch the different records from
    the European Nucleotide Archive (https://www.ebi.ac.uk/ena/portal/home)
    using its REST API

    Class variables
    ---------------
    url : string
          the url used to connect the ENA:
          {CONFIG.get('ena_portal', 'endpoint')}
    """
    def __init__(self):

        enaportal_logger.debug('Creating an ENAportal object')
        self.url = f"{CONFIG.get('ena_portal', 'endpoint')}"
