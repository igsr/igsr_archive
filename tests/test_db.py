import pytest
import logging
import os
import pdb

from igsr_archive.db import DB
from igsr_archive.file import File

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def del_obj(db_obj):

    fileList = []
    yield fileList

    log = logging.getLogger('del_f')
    log.debug('Delete File from DB')

    for fO in fileList:
        db_obj.delete_file(fO,
                           dry=False)


def test_conn_s():
    log = logging.getLogger('test_conn_s')
    log.debug('Testing connection with valid credentials and DB name')

    pwd = os.getenv('DBPWD')
    dbname = os.getenv('DBNAME')

    assert dbname, "$DBNAME undefined"
    assert pwd, "$PWD undefined"

    db = DB(pwd=pwd,
            dbname=dbname)

    assert db.conn

def test_conn_e():
    log = logging.getLogger('test_conn_e')
    log.debug('Testing connection with non valid credentials')

    dbname = os.getenv('DBNAME')
    assert dbname, "$DBNAME undefined"

    with pytest.raises(Exception) as e_info:
        db = DB(pwd="mockpwd",
                dbname=dbname)

def test_load_f(db_obj, del_obj):
    log = logging.getLogger('test_load_f')

    log.debug('Testing \'load_file\' function to load file entry in DB')

    f = File(
        name=os.getenv('DATADIR')+"/test.txt",
        type="TYPE_F"
    )

    db_obj.load_file(f, dry=False)

    del_obj.append(f)

def test_update_f(db_obj, del_obj):
    log = logging.getLogger('test_update_f')

    log.debug("Testing \'update_file\' function to update an entry "
              "in the \'file\' table of the DB")

    # First, load file entry in the database
    f = File(
        name=os.getenv('DATADIR')+"/test.txt",
        type="TYPE_F")

    db_obj.load_file(f, dry=False)

    # Now, modify the file path for
    # entry in the 'file' table
    db_obj.update_file(attr_name='name',
                       value=os.getenv('DATADIR')+"test1.txt",
                       name=os.getenv('DATADIR')+"test.txt",
                       dry=False)

    f1 = File(
        name=os.getenv('DATADIR')+"test1.txt",
        type="TYPE_F")

    del_obj.append(f1)

def test_delete_f(db_obj):
    log = logging.getLogger('test_delete_f')

    log.debug('Testing \'delete_file\' function to delete a file entry in the DB')

    f = File(
        name=os.getenv('DATADIR')+"/test.txt",
        type="TYPE_F"
    )

    # Load file in db before deleting it
    db_obj.load_file(f, dry=False)

    # Now, delete it
    db_obj.delete_file(f, dry=False)

def test_fetch_f_exists_w_path(db_obj, del_obj):
    log = logging.getLogger('test_fetch_f_exists_w_path')

    log.debug('Testing \'fetch_file\' function to fetch an existing'
              'file from the DB using its path')

    rel_path = os.getenv('DATADIR')+"/test.txt"
    # First, load file entry in the database
    f = File(
        name=rel_path,
        type="TYPE_F")

    db_obj.load_file(f, dry=False)

    # path provided here points to the loaded file
    rf = db_obj.fetch_file(path=rel_path)

    del_obj.append(rf)

    assert rf.name == os.path.abspath(rel_path)


def test_fetch_f_not_exists_w_path(db_obj):
    log = logging.getLogger('test_fetch_f_not_exists_w_path')

    log.debug('Testing \'fetch_file\' function to fetch a non-existing'
              'file from the DB using its path')

    # path provided here points to an existing file
    f = db_obj.fetch_file(path='mock_file.txt')

    assert f == None

def test_fetch_f_exists_w_basename(db_obj, del_obj):
    log = logging.getLogger('test_fetch_f_exists_w_basename')

    log.debug('Testing \'fetch_file\' function to fetch an existing'
              'file from the DB using its basename')

    rel_path = os.getenv('DATADIR')+"/test.txt"

    # First, load file entry in the database
    f = File(
        name=rel_path,
        type="TYPE_F")

    db_obj.load_file(f, dry=False)

    # path provided here points to an existing file
    f = db_obj.fetch_file(basename='test.txt')

    del_obj.append(f)

    assert f.name == os.path.abspath(rel_path)

def test_fetch_f_not_exists_w_basename(db_obj):
    log = logging.getLogger('test_fetch_f_not_exists_w_basename')

    log.debug('Testing \'fetch_file\' function to fetch a non-existing'
              'file from the DB using its basename')

    # path provided here points to an existing file
    f = db_obj.fetch_file(basename='mock_file.txt')

    assert f == None

def test_get_ctree(db_obj):
    log = logging.getLogger('test_get_ctree_l')

    log.debug('Testing \'get_ctree\' function to get the current.same.tree file'
              'from the DB limiting the number of dumped records')

    # list of fields in the 'file' table
    # to be dumped in the current.same.tree file
    fields = ['name', 'size', 'updated', 'md5']
    ctree_path, data_dict = db_obj.get_ctree(fields, outfile= os.getenv('DATADIR')+"/current.same.tree", limit=10)
    assert os.path.exists(ctree_path == 1)
    assert len(data_dict.keys()) == 10

