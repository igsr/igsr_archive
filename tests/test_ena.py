import pytest
import logging

logging.basicConfig(level=logging.DEBUG)

def test_fetch_run():
    
    log = logging.getLogger('test_retrieve_object_by_foi')

    log.debug('Retrieving (Downloading) a FIRE object by its fireOid')

