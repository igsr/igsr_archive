import pytest
import logging
import os
import pdb

from reseqtrack.db import DB
from file.file import File

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def db_obj():
    """
    Fixture to get a DB object
    """

    pwd = os.getenv('DBPWD')
    dbname = os.getenv('DBNAME')

    assert dbname, "$DBNAME undefined"
    assert pwd, "$PWD undefined"

    db = DB(settingf="../../data/settings.ini",
            pwd=pwd,
            dbname=dbname)

    return db


def test_conn_s():
    log = logging.getLogger('test_conn_s')
    log.debug('Testing connection with valid credentials and DB name')

    pwd = os.getenv('DBPWD')
    dbname = os.getenv('DBNAME')

    assert dbname, "$DBNAME undefined"
    assert pwd, "$PWD undefined"

    db = DB(settingf="../../data/settings.ini",
            pwd=pwd,
            dbname=dbname)

    assert db.conn

def test_conn_e():
    log = logging.getLogger('test_conn_e')
    log.debug('Testing connection with non valid credentials')

    dbname = os.getenv('DBNAME')
    assert dbname, "$DBNAME undefined"

    with pytest.raises(Exception) as e_info:
        db = DB(settingf="../../data/settings.ini",
                pwd="mockpwd",
                dbname=dbname)

def test_load_f(db_obj):
    log = logging.getLogger('test_load_f')

    log.debug('Testing \'load_file\' function to load file in DB')

    f = File(
        name="../../data/test.txt",
        type="TYPE_F"
    )

    db_obj.load_file(f, dry=False)

def test_delete_f(db_obj):
    log = logging.getLogger('test_delete_f')

    log.debug('Testing \'delete_file\' function to delete a file in the DB')

    f = File(
        name="../../data/test.txt",
        type="TYPE_F"
    )

    # Load file in db before deleting it
    db_obj.load_file(f, dry=False)

    # Now, delete it
    db_obj.delete_file(f, dry=False)

def test_fetch_f_exists(db_obj):
    log = logging.getLogger('test_fetch_f_exists')

    log.debug('Testing \'fetch_file\' function to fetch an existing'
              'file from the DB')

    # path provided here points to an existing file
    f = db_obj.fetch_file('/nfs/1000g-archive/vol1/ftp/current.tree')

    assert f.name == '/nfs/1000g-archive/vol1/ftp/current.tree'


def test_fetch_f_not_exists(db_obj):
    log = logging.getLogger('test_fetch_f_not_exists')

    log.debug('Testing \'fetch_file\' function to fetch a non-existing'
              'file from the DB')

    # path provided here points to an existing file
    f = db_obj.fetch_file('mock_file.txt')

    assert f == None