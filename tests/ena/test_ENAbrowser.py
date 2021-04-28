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

def test_fetch_attrbs():

    log = logging.getLogger('test_fetch_attrbs')

    log.debug('Fetch the {type}_ATTRIBUTES')

    ebrowser = ENAbrowser(acc="SAMN00001598")
    xmld = ebrowser.query()

    a_dict = ebrowser.fetch_attrbs('SAMPLE', xmld)

    assert len(a_dict.keys()) == 14

def test_fetch_attrbs_w_alist():

    log = logging.getLogger('test_fetch_attrbs_w_alist')

    log.debug('Fetch the {type}_ATTRIBUTES with the alist parameter')

    ebrowser = ENAbrowser(acc="SAMN00001598")
    xmld = ebrowser.query()

    a_dict = ebrowser.fetch_attrbs('SAMPLE', xmld, alist= ['population', 'Super Population Code'])

    assert len(a_dict.keys()) == 2

def test_fetch_xrefs_run():

    log = logging.getLogger('test_fetch_xrefs_run')

    log.debug('Fetch the XREF_LINK attributes for a particular run accession')

    ebrowser = ENAbrowser(acc="ERR001386")
    xmld = ebrowser.query()

    a_dict = ebrowser.fetch_xrefs('RUN', xmld)

    assert len(list(a_dict.keys())) == 5

def test_fetch_xrefs_analysis():

    log = logging.getLogger('test_fetch_xrefs_analysis')

    log.debug('Fetch the XREF_LINK attributes for a particular analysis accession')

    ebrowser = ENAbrowser(acc="ERZ1669093")
    xmld = ebrowser.query()

    a_dict = ebrowser.fetch_xrefs('ANALYSIS', xmld)

    assert a_dict['ENA-SUBMISSION'] == 'ERA3062116'