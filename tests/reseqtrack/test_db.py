import pytest
import logging
import os

from reseqtrack.db import DB

logging.basicConfig(level=logging.DEBUG)

def test_conn_s():
    log = logging.getLogger('test_conn_s')
    log.debug('Testing connection with valid credentials and DB name')

    pwd = os.getenv('PWD')
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
