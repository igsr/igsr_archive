import pytest
import logging
import os
import glob
import pdb

from fire.api import API

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def clean_tmp():
    yield
    print("Cleanup files")
    files = glob.glob('../../data/out/*')
    for f in files:
        os.remove(f)

def test_retrieve_object_by_foi(clean_tmp):
    log = logging.getLogger('test_retrieve_object_by_foi')

    log.debug('Retrieving (Downloading) a FIRE object by its fireOid')
    pwd = os.getenv('FIRE_PWD')
    username = os.getenv('USERNAME')

    assert pwd, "$FIRE_PWD undefined"
    assert username, "$USERNAME undefined"

    api = API(settingsf="../../data/settings.ini",
              user=username,
              pwd=pwd)

    outfile = api.retrieve_object(fireOid='14a851b68de08d0bdcd1069107d9130f',
                                  outfile='../../data/out/out.pdf')

    assert outfile == "../../data/out/out.pdf"

def test_retrieve_object_by_fpath(clean_tmp):
    log = logging.getLogger('test_retrieve_object_by_fpath')

    log.debug('Retrieving (Downloading) a FIRE object by its firePath')
    pwd = os.getenv('FIRE_PWD')
    username = os.getenv('USERNAME')

    assert pwd, "$FIRE_PWD undefined"
    assert username, "$USERNAME undefined"

    api = API(settingsf="../../data/settings.ini",
              user=username,
              pwd=pwd)

    outfile = api.retrieve_object(firePath='ftp/data_collections/gambian_genome_variation_project/'
                                           'release/20200217_biallelic_SNV/'
                                           'README_gambian_genome_variation_project_biallelic_SNV_INDEL_callset.pdf',
                                  outfile='../../data/out/out.pdf')

    assert outfile == "../../data/out/out.pdf"

def test_fetch_object_by_foi():
    log = logging.getLogger('test_fetch_object_by_foi')

    log.debug('Fetching metadata for a particular FIRE object by its fireOid')
    pwd = os.getenv('FIRE_PWD')
    username = os.getenv('USERNAME')

    assert pwd, "$FIRE_PWD undefined"
    assert username, "$USERNAME undefined"

    api = API(settingsf="../../data/settings.ini",
              user=username,
              pwd=pwd)

    fobject = api.fetch_object(fireOid='14a851b68de08d0bdcd1069107d9130f')

    assert 0
