import pytest
import logging

from igsr_archive.ena_api import ENA

logging.basicConfig(level=logging.DEBUG)

def test_get_run_by_id():
    
    log = logging.getLogger('test_get_run_by_id')

    log.debug('Fetch ENA RUN record via its id')

    ena=ENA()
    ena.get_run_by_id("ERR4968409")

