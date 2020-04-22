import pytest
import logging
import datetime

from file.file import File

logging.basicConfig(level=logging.DEBUG)

def test_f_w_md5():
    log = logging.getLogger('test_f_w_md5')
    log.debug('Instantiation with md5sum')

    f = File(
        path="../../data/test.txt",
        type="TEST_F",
        md5sum="f5aa4f4f1380b71acc56750e9f8ff825")

    assert f.md5sum == "f5aa4f4f1380b71acc56750e9f8ff825"

def test_f_wo_md5():
    log = logging.getLogger('test_f_wo_md5')
    log.debug('Instantiation without md5sum')

    f = File(
        path="../../data/test.txt",
        type="TYPE_F"
    )

    assert f.md5sum == "f5aa4f4f1380b71acc56750e9f8ff825"

def test_f_w_size():
    log = logging.getLogger('test_f_w_size')
    log.debug('Instantiation with file size')

    f = File(
        path="../../data/test.txt",
        type="TYPE_F",
        size=17)

    assert f.size == 17

def test_f_wo_size():
    log = logging.getLogger('test_f_wo_size')
    log.debug('Instantiation without file size')

    f = File(
        path="../../data/test.txt",
        type="TYPE_F"
        )

    assert f.size == 17

def test_f_wo_creation_date():
    log = logging.getLogger('test_f_wo_creation_date')
    log.debug('Instantiation without creation date')

    f = File(
        path="../../data/test.txt",
        type="TYPE_F"
    )

    assert f.created == datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')