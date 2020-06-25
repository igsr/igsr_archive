import logging
import datetime

from igsr_archive.file import File

logging.basicConfig(level=logging.DEBUG)

def test_f_w_md5():
    log = logging.getLogger('test_f_w_md5')
    log.debug('Instantiation with md5sum')

    f = File(
        name="../data/test.txt",
        type="TEST_F",
        md5="f5aa4f4f1380b71acc56750e9f8ff825")

    assert f.md5 == "f5aa4f4f1380b71acc56750e9f8ff825"

def test_f_wo_md5():
    log = logging.getLogger('test_f_wo_md5')
    log.debug('Instantiation without md5sum')

    f = File(
        name="../data/test.txt",
        type="TYPE_F"
    )

    assert f.md5 == "f5aa4f4f1380b71acc56750e9f8ff825"

def test_f_w_size():
    log = logging.getLogger('test_f_w_size')
    log.debug('Instantiation with file size')

    f = File(
        name="../data/test.txt",
        type="TYPE_F",
        size=17)

    assert f.size == 17

def test_f_wo_size():
    log = logging.getLogger('test_f_wo_size')
    log.debug('Instantiation without file size')

    f = File(
        name="../data/test.txt",
        type="TYPE_F"
        )

    assert f.size == 17

def test_f_wo_creation_date():
    log = logging.getLogger('test_f_wo_creation_date')
    log.debug('Instantiation without creation date')

    f = File(
        name="../data/test.txt",
        type="TYPE_F"
    )

    assert f.created == datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
def test_check_if_exists():
    log = logging.getLogger('test_check_if_exists')
    log.debug('Testing function for checking if a file exists')

    f = File(
        name="../data/test.txt",
        type="TYPE_F"
    )

    assert f.check_if_exists() is True

def test_guess_type():
    log = logging.getLogger('test_guess_type')
    log.debug('Testing function for guess the type of a file')

    f = File(name="../data/test.txt",
             settingf="../data/settings.ini")
    assert f.guess_type() == "TEST_TXT"

