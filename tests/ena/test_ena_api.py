import pytest
import logging

from igsr_archive.ena.ena_query import ENAquery, ENAbrowser

logging.basicConfig(level=logging.DEBUG)

TODO: refactor from ENAquery to ENA
def test_ENAquery_query():
    log = logging.getLogger('test_ENAquery_query')

    log.debug('Test the query function from ENAquery')

    equery = ENAquery(url="https://www.ebi.ac.uk/ena/browser/api/xml/ERR001386")
    res = equery.query()

    assert res.status_code == 200

def test_ENAbrowser_query():
    log = logging.getLogger('test_ENAbrowser_query')

    log.debug('Test the query function from ENAbrowser')

    ebrowser = ENAbrowser(acc="ERR001386")

    xmld = ebrowser.query()

    assert 0

"""
def test_get_run_by_id():
    
    log = logging.getLogger('test_get_run_by_id')

    log.debug('Fetch ENA RUN record via its id')

    ena=ENA()
    ena.get_run_by_id("ERR000044")

def test_get_study_by_id():
    
    log = logging.getLogger('test_get_study_by_id')

    log.debug('Fetch ENA STUDY record via its id')

    ena=ENA()
    ena.get_study_by_id("ERP125611")
"""