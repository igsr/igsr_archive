import pytest
import logging
import os
import glob
import pdb

from fire.api import API
from file.file import File

logging.basicConfig(level=logging.DEBUG)

pwd = os.getenv('FIRE_PASSWORD')

assert pwd, "$FIRE_PWD undefined"

api = API(settingsf="../../data/settings.ini",
          pwd=pwd)

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

    outfile = api.retrieve_object(fireOid='423ad6c276b440cdaee47ad44fb62d35',
                                  outfile='../../data/out/test.txt')

    assert outfile == "../../data/out/test.txt"

def test_retrieve_object_by_fpath(clean_tmp):
    log = logging.getLogger('test_retrieve_object_by_fpath')

    log.debug('Retrieving (Downloading) a FIRE object by its firePath')

    outfile = api.retrieve_object(firePath='/test_dir/test.txt',
                                  outfile='../../data/out/test.txt')

    assert outfile == "../../data/out/test.txt"

def test_fetch_object_by_foi():
    log = logging.getLogger('test_fetch_object_by_foi')

    log.debug('Fetching metadata for a particular FIRE object by its fireOid')

    fobject = api.fetch_object(fireOid='423ad6c276b440cdaee47ad44fb62d35')

    assert fobject.fireOid == '423ad6c276b440cdaee47ad44fb62d35'
    assert fobject.objectId == 91263

def test_fetch_object_by_fpath():
    log = logging.getLogger('test_fetch_object_by_fpath')

    log.debug('Fetching metadata for a particular FIRE object by its firePath')

    fobject = api.fetch_object(firePath='/test_dir/test.txt')

    assert fobject.fireOid == '423ad6c276b440cdaee47ad44fb62d35'
    assert fobject.objectId == 91263

def test_delete_object_by_foi():
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_delete_object_by_foi')

    log.debug('Deleting a FIRE object using its fireOid')

    # first, push a test file to FIRE
    # creating File object
    f = File(
        path="../../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fireObj = api.push_object(fileO=f, dry=False,
                              fire_path="test_dir/test.txt")

    # now, you can delete it by its fireOid
    api.delete_object(fireOid=fireObj.fireOid, dry=False)

def test_push_object():
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_push_object')

    log.debug('Pushing (upload) a file.file.File object to FIRE')

    # creating File object
    f = File(
        path="../../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    api.push_object(fileO=f, dry=True)

def test_push_object_w_fpath():
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_push_object_w_fpath')

    log.debug('Pushing (upload) a file.file.File object to FIRE adding a '
              'virtual FIRE path')

    # creating File object
    f = File(
        path="../../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    api.push_object(fileO=f, dry=True,
                    fire_path="test_dir/test.txt")



