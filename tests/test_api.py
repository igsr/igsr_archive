import pytest
import logging
import os
import glob
import pdb

from igsr_archive.api import API
from igsr_archive.file import File

logging.basicConfig(level=logging.DEBUG)

pwd = os.getenv('FIRE_PWD')

assert pwd, "$FIRE_PWD undefined"

api = API(settingsf="../data/settings.ini",
          pwd=pwd)

@pytest.fixture
def clean_tmp():
    yield
    log = logging.getLogger('clean_tmp')
    log.debug('Cleaning tmp files')

    files = glob.glob('../data/out/*')
    for f in files:
        os.remove(f)

@pytest.fixture
def loaded_obj():

    log = logging.getLogger('loaded_obj')
    log.debug('push FIRE object')

    # creating File object
    f = File(
        name="../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fobject = api.push_object(fileO=f, dry=False,
                              fire_path="test_dir/test.txt")

    return fobject

@pytest.fixture
def del_obj():

    fireOids = []
    yield fireOids

    log = logging.getLogger('del_obj')
    log.debug('Delete FIRE object')

    for fid in fireOids:
        api.delete_object(fireOid=fid,
                          dry=False)

def test_retrieve_object_by_foi(loaded_obj, del_obj, clean_tmp):
    log = logging.getLogger('test_retrieve_object_by_foi')

    log.debug('Retrieving (Downloading) a FIRE object by its fireOid')

    outfile = api.retrieve_object(fireOid=loaded_obj.fireOid,
                                  outfile='../data/out/test.txt')

    del_obj.append(loaded_obj.fireOid)

    assert outfile == "../data/out/test.txt"

def test_retrieve_object_by_fpath(loaded_obj, del_obj, clean_tmp):
    log = logging.getLogger('test_retrieve_object_by_fpath')

    log.debug('Retrieving (Downloading) a FIRE object by its firePath')

    outfile = api.retrieve_object(firePath='test_dir/test.txt',
                                  outfile='../data/out/test.txt')

    del_obj.append(loaded_obj.fireOid)

    assert outfile == "../data/out/test.txt"

def test_fetch_object_by_foi(loaded_obj, del_obj):
    log = logging.getLogger('test_fetch_object_by_foi')

    log.debug('Fetching metadata for a particular FIRE object by its fireOid')
    fobject = api.fetch_object(fireOid=loaded_obj.fireOid)

    del_obj.append(loaded_obj.fireOid)

    assert fobject.fireOid == loaded_obj.fireOid
    assert fobject.objectId == loaded_obj.objectId

def test_fetch_object_by_fpath(loaded_obj, del_obj):
    log = logging.getLogger('test_fetch_object_by_fpath')

    log.debug('Fetching metadata for a particular FIRE object by its firePath')

    fobject = api.fetch_object(firePath='test_dir/test.txt')

    del_obj.append(loaded_obj.fireOid)

    assert fobject.objectMd5 == 'f5aa4f4f1380b71acc56750e9f8ff825'
    assert fobject.objectSize == 17

def test_fetch_nonexistent_object_by_fpath():
    log = logging.getLogger('test_fetch_nonexistent_object_by_fpath')

    log.debug('Fetching metadata for a non-existent FIRE object')

    fobject = api.fetch_object(firePath='test_dir/mockfile.txt')

    assert fobject == None

def test_delete_object_by_foi(loaded_obj):
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_delete_object_by_foi')

    log.debug('Deleting a FIRE object using its fireOid')

    # now, you can delete it by its fireOid
    api.delete_object(fireOid=loaded_obj.fireOid, dry=False)

def test_push_object(del_obj):
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_push_object')

    log.debug('Pushing (upload) a file.file.File object to FIRE')

    # creating File object
    f = File(
        name="../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fobj = api.push_object(fileO=f, dry=False)

    del_obj.append(fobj.fireOid)

def test_push_object_w_fpath(del_obj):
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_push_object_w_fpath')

    log.debug('Pushing (upload) a file.file.File object to FIRE adding a '
              'virtual FIRE path')

    # creating File object
    f = File(
        name="../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fobj = api.push_object(fileO=f, dry=False,
                           fire_path="test_dir/test.txt")

    del_obj.append(fobj.fireOid)

def test_push_comp_object_w_fpath(del_obj):
    """
    Test used to check if 'push_object' works
    also with a *.gz compressed file
    """
    log = logging.getLogger('test_push_comp_object_w_fpath')

    log.debug('Pushing (upload) a compressed file.file.File object to FIRE adding a '
              'virtual FIRE path')

    # creating File object
    f = File(
        name="../data/test.txt.gz",
        type="TEST_F",
        md5sum="a32c5f11391b49b0788def64d28f8807")

    fobj = api.push_object(fileO=f, dry=False,
                           fire_path="test_dir/test.txt.gz")

    del_obj.append(fobj.fireOid)


def test_update_object(loaded_obj, del_obj):
    """
    This test will test the 'update_object' function
    to update the FIRE path of an archived object
    """

    log = logging.getLogger('test_update_object')

    log.debug('Updating FIRE path of an archived'
              ' object')

    updated_obj = api.update_object(attr_name='firePath',
                                    value='test_dir1/test.txt',
                                    fireOid=loaded_obj.fireOid,
                                    dry=False)

    # check that FIRE path has been modified
    assert updated_obj.path == "/test_dir1/test.txt"

    del_obj.append(loaded_obj.fireOid)

