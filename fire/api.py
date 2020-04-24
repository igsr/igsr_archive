import logging

# create logger
api_logger = logging.getLogger(__name__)


class API(object):
    """
    Class to deal with the queries to the FIRE API for
    archival and retrieval activities

    Class variables
    ---------------

    """
    def __init__(self, **kwargs):

        api_logger.info('Creating a Fire Object')

