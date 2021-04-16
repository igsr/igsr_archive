import pytest
import logging

from igsr_archive.ena.ena_query import ENAbrowser

logging.basicConfig(level=logging.DEBUG)

def test_ENAbrowser_query():
    log = logging.getLogger('test_ENAbrowser_query')

    log.debug('Test the query function from ENAbrowser')

    ebrowser = ENAbrowser(acc="ERR001386")

    xmld = ebrowser.query()
    assert list(xmld.keys())[0] == 'RUN_SET'

def test_get_record():
    
    log = logging.getLogger('test_get_record')

    log.debug('Fetch ENArecord using its accession id')

    ebrowser = ENAbrowser(acc="ERR001386")
    xmld = ebrowser.query()
    ena_record = ebrowser.get_record(xmld)

    assert ena_record.type == 'RUN'
    assert ena_record.primary_id == 'ERR001386'