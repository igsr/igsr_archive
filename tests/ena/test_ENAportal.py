import pytest
import logging

from igsr_archive.ena.ena_query import ENAportal

logging.basicConfig(level=logging.DEBUG)

def test_ENAportal_query_run():
    log = logging.getLogger('test_ENAportal_query_run')

    log.debug('Test the query function from ENAportal to fetch a file record for a particular run acc')

    eportal = ENAportal(acc="ERR001386")

    record_lst = eportal.query()

    assert record_lst[0].accession == "ERR001386"

def test_ENAportal_query_analysis():
    log = logging.getLogger('test_ENAportal_query_analysis')

    log.debug('Test the query function from ENAportal to fetch a file record for a particular run acc')

    eportal = ENAportal(acc="ERZ1669096")

    record_lst = eportal.query(q_type='analysis')

    assert record_lst[0].accession == "ERZ1669096"

def test_ENAportal_query_fields():
    log = logging.getLogger('test_ENAportal_query_fields')

    log.debug('Test the query function from ENAportal to fetch a file record selecting a certain number of fields')

    eportal = ENAportal(acc="ERR001386")

    record_lst = eportal.query(fields='run_accession,fastq_ftp,fastq_md5')

    assert sorted(list(record_lst[0].__dict__.keys())) == ['accession', 'fastq_ftp', 'fastq_md5', 'type']
