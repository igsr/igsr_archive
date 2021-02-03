import pytest
import logging
import os
import glob
import pdb
import responses

from igsr_archive.object import fObject
from igsr_archive.api import API
from igsr_archive.file import File

logging.basicConfig(level=logging.DEBUG)

pwd = os.getenv('FIREPWD')

assert pwd, "$FIREPWD undefined"

api = API(pwd=pwd)

@pytest.fixture
def clean_tmp():
    yield
    log = logging.getLogger('clean_tmp')
    log.debug('Cleaning tmp files')

    files = glob.glob(os.getenv('DATADIR')+'/out/*')
    for f in files:
        os.remove(f)

@pytest.fixture
def loaded_obj():

    log = logging.getLogger('loaded_obj')
    log.debug('push FIRE object')

    # creating File object
    f = File(
        name=os.getenv('DATADIR')+"/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fobject = api.push_object(fileO=f, dry=False,
                              fire_path="test_dir/test.txt",
                              publish=False)
    return fobject

@pytest.fixture
def mock_fireobj():
    """
    Object mimicking a file archived in FIRE
    """

    f_obj = fObject(objectId=61903465,
                    fireOid='06cb664f1b844809b09a93cb18fcfc6b',
                    objectMd5='369ccfaf31586363bd645d48b72c09c4',
                    objectSize='7',
                    createTime='2021-02-02 11:53:01',
                    path='/test_dir/test.txt',
                    published='False')

    return f_obj

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
                                  outfile=os.getenv('DATADIR')+'/out/test.txt')

    del_obj.append(loaded_obj.fireOid)

    assert outfile == os.getenv('DATADIR')+"/out/test.txt"

def test_retrieve_object_by_fpath(loaded_obj, del_obj, clean_tmp):
    log = logging.getLogger('test_retrieve_object_by_fpath')

    log.debug('Retrieving (Downloading) a FIRE object by its firePath')

    outfile = api.retrieve_object(firePath='test_dir/test.txt',
                                  outfile=os.getenv('DATADIR')+"/out/test.txt")

    del_obj.append(loaded_obj.fireOid)

    assert outfile == os.getenv('DATADIR')+"/out/test.txt"

@responses.activate
def test_fetch_object_by_foi(mock_fireobj):
    log = logging.getLogger('test_fetch_object_by_foi')

    log.debug('Fetching metadata for a particular FIRE object by its fireOid')

    responses.add(responses.GET, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b',
                  json= {'objectId': 61903465,
                         'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                         'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                         'objectSize': 7,
                         'createTime': '2021-02-02 11:53:01',
                         'metadata': [],
                         'filesystemEntry': None},
                  status=200)

    ret_fobject = api.fetch_object(fireOid=mock_fireobj.fireOid)

    assert mock_fireobj.fireOid == ret_fobject.fireOid
    assert mock_fireobj.objectId == ret_fobject.objectId

@responses.activate
def test_fetch_object_by_fpath(mock_fireobj):
    log = logging.getLogger('test_fetch_object_by_fpath')

    log.debug('Fetching metadata for a particular FIRE object by its firePath')

    responses.add(responses.GET, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/path/test_dir/test.txt',
                  json= {'objectId': 61903465,
                         'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                         'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                         'objectSize': 7,
                         'createTime': '2021-02-02 11:53:01',
                         'metadata': [],
                         'filesystemEntry': {'path': '/test_dir/test.txt',
                                             'published': False}}, status=200)

    ret_fobject = api.fetch_object(firePath='test_dir/test.txt')

    assert mock_fireobj.fireOid == ret_fobject.fireOid
    assert mock_fireobj.objectId == ret_fobject.objectId

@responses.activate
def test_fetch_nonexistent_object_by_fpath():
    log = logging.getLogger('test_fetch_nonexistent_object_by_fpath')

    log.debug('Fetching metadata for a non-existent FIRE object')

    responses.add(responses.GET, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/path/test_dir/mockfile.txt',
                  json={'statusCode': 404,
                        'statusMessage': 'Not Found',
                        'httpMethod': 'GET',
                        'detail': 'No archived object found which has a Fire path of `/test_dir/mockfile.txt`'},
                  status=404)

    ret_fobject = api.fetch_object(firePath='test_dir/mockfile.txt')

    assert ret_fobject == None

@responses.activate
def test_delete_object_by_foi(mock_fireobj):
    """
    This test will fail if an Exception is raised
    """
    log = logging.getLogger('test_delete_object_by_foi')

    responses.add(responses.DELETE, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b',
                  json={},
                  status=204)

    log.debug('Deleting a FIRE object using its fireOid')

    # now, you can delete it by its fireOid
    api.delete_object(fireOid=mock_fireobj.fireOid, dry=False)

def test_push_object(del_obj):
    """
    This test will fail if an Exception is raised
    The push_object will be invoked without fire_path and will not publish
    """
    log = logging.getLogger('test_push_object')

    log.debug('Pushing (upload) a file.file.File object to FIRE')

    # creating File object
    f = File(
        name=os.getenv('DATADIR')+"/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fobj = api.push_object(fileO=f, dry=False, publish=False)

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
        name=os.getenv('DATADIR')+"test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    fobj = api.push_object(fileO=f, dry=False, publish=False,
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
        name=os.getenv('DATADIR')+"test.txt.gz",
        type="TEST_F",
        md5sum="a32c5f11391b49b0788def64d28f8807")

    fobj = api.push_object(fileO=f, dry=False,
                           fire_path="test_dir/test.txt.gz")

    del_obj.append(fobj.fireOid)

@responses.activate
def test_update_object_w_fpath(mock_fireobj):
    """
    This test will test the 'update_object' function
    to update the FIRE path of an archived object
    """

    log = logging.getLogger('test_update_object_w_fpath')

    log.debug('Updating FIRE path of an archived'
              ' object')

    responses.add(responses.GET, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b',
                  json={'objectId': 61903465,
                        'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                        'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                        'objectSize': 7,
                        'createTime': '2021-02-02 11:53:01',
                        'metadata': [],
                        'filesystemEntry': {'path': '/test_dir/test.txt',
                                            'published': False}},
                  status=200)

    responses.add(responses.PUT, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b/firePath',
                  json={'objectId': 61903465,
                        'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                        'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                        'objectSize': 7,
                        'createTime': '2021-02-02 11:53:01',
                        'metadata': [],
                        'filesystemEntry': {'path': '/test_dir1/test.txt',
                                            'published': False}},
                  headers={'x-fire-path': 'test_dir1/test.txt'},
                  status=200)

    updated_obj = api.update_object(attr_name='firePath',
                                    value='test_dir1/test.txt',
                                    fireOid=mock_fireobj.fireOid,
                                    dry=False)

    # check that FIRE path has been modified
    assert updated_obj.path == "/test_dir1/test.txt"

@responses.activate
def test_update_object_publish1(mock_fireobj):
    """
    This test will test the 'update_object' function
    to change publish status of an archived object
    """

    log = logging.getLogger('test_update_object_publish1')

    log.debug('Updating FIRE object metadata. Publish will be set '
              'to True')

    responses.add(responses.GET, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b',
                  json={'objectId': 61903465,
                        'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                        'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                        'objectSize': 7,
                        'createTime': '2021-02-02 11:53:01',
                        'metadata': [],
                        'filesystemEntry': {'path': '/test_dir/test.txt',
                                            'published': False}},
                  status=200)

    responses.add(responses.PUT,
                  'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b/publish',
                  json={'objectId': 61903465,
                        'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                        'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                        'objectSize': 7,
                        'createTime': '2021-02-02 11:53:01',
                        'metadata': [],
                        'filesystemEntry': {'path': '/test_dir/test.txt',
                                            'published': True}},
                  status=200)

    updated_obj = api.update_object(attr_name='publish',
                                    value=True,
                                    fireOid=mock_fireobj.fireOid,
                                    dry=False)

    # check that FIRE path has been modified
    assert updated_obj.published is True

@responses.activate
def test_update_object_publish2(mock_fireobj):
    """
    This test will test the 'update_object' function
    to change publish status of an archived object
    """

    log = logging.getLogger('test_update_object_publish2')

    log.debug('Updating FIRE object metadata. Publish will be set '
              'to False')

    responses.add(responses.GET, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b',
                  json={'objectId': 61903465,
                        'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                        'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                        'objectSize': 7,
                        'createTime': '2021-02-02 11:53:01',
                        'metadata': [],
                        'filesystemEntry': {'path': '/test_dir/test.txt',
                                            'published': False}},
                  status=200)

    responses.add(responses.DELETE, 'https://hx.fire.sdo.ebi.ac.uk/fire/v1.1/objects/06cb664f1b844809b09a93cb18fcfc6b/publish',
                  json={'objectId': 61903465,
                        'fireOid': '06cb664f1b844809b09a93cb18fcfc6b',
                        'objectMd5': '369ccfaf31586363bd645d48b72c09c4',
                        'objectSize': 7,
                        'createTime': '2021-02-02 11:53:01',
                        'metadata': [],
                        'filesystemEntry': {'path': '/test_dir/test.txt',
                                            'published': False}},
                  status=200)

    updated_obj = api.update_object(attr_name='publish',
                                    value=False,
                                    fireOid=mock_fireobj.fireOid,
                                    dry=False)

    # check that FIRE path has been modified
    assert updated_obj.published is False