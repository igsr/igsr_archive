import pytest
import logging

from igsr_archive.ena.ena_query import ENA

logging.basicConfig(level=logging.DEBUG)

def test_ENA_query():
    log = logging.getLogger('test_ENA_query')

    log.debug('Test the query function from ENA')

    ena = ENA(url="https://www.ebi.ac.uk/ena/browser/api/xml/ERR001386")
    res = ena.query()

    assert res.status_code == 200

