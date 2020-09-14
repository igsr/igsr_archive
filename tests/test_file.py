import logging
import datetime
import os
import pdb

from igsr_archive.file import File

logging.basicConfig(level=logging.DEBUG)

def test_f_w_md5():
    log = logging.getLogger('test_f_w_md5')
    log.debug('Instantiation with md5sum')

    f = File(
        name=f"{os.getenv('DATADIR')}/test.txt",
        type="TEST_F",
        md5="369ccfaf31586363bd645d48b72c09c4")

    assert f.md5 == "369ccfaf31586363bd645d48b72c09c4"

def test_f_wo_md5():
    log = logging.getLogger('test_f_wo_md5')
    log.debug('Instantiation without md5sum')
    f = File(
        name=f"{os.getenv('DATADIR')}/test.txt",
        type="TYPE_F"
    )

    assert f.md5 == "369ccfaf31586363bd645d48b72c09c4"

def test_f_w_size():
    log = logging.getLogger('test_f_w_size')
    log.debug('Instantiation with file size')

    f = File(
        name=f"{os.getenv('DATADIR')}/test.txt",
        type="TYPE_F",
        size=7)

    assert f.size == 7

def test_f_wo_size():
    log = logging.getLogger('test_f_wo_size')
    log.debug('Instantiation without file size')

    f = File(
        name=f"{os.getenv('DATADIR')}/test.txt",
        type="TYPE_F"
        )

    assert f.size == 7

def test_f_wo_creation_date():
    log = logging.getLogger('test_f_wo_creation_date')
    log.debug('Instantiation without creation date')

    f = File(
        name=f"{os.getenv('DATADIR')}/test.txt",
        type="TYPE_F"
    )

    assert f.created == datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
def test_check_if_exists():
    log = logging.getLogger('test_check_if_exists')
    log.debug('Testing function for checking if a file exists')

    f = File(
        name=f"{os.getenv('DATADIR')}/test.txt",
        type="TYPE_F"
    )

    assert f.check_if_exists() is True

def test_guess_type(settings_f):
    log = logging.getLogger('test_guess_type')
    log.debug('Testing function for guess the type of a file')

    f = File(name=f"{os.getenv('DATADIR')}/test.txt",
             settingsf=settings_f)
    assert f.guess_type() == "TEST_TXT"

def test_guess_type1(settings_f, rand_file):
    log = logging.getLogger('test_guess_type1')
    log.debug('Testing function for guess the type of a complex filename')
    new_fname = f"{os.getenv('DATADIR')}/test_arch.2020.txt"
    # change the basename to something more complex
    os.rename(f"{os.getenv('DATADIR')}/test_arch.txt", new_fname)
    f = File(name=new_fname,
             settingsf=settings_f)

    # delete test type
    os.remove(new_fname)
    assert f.guess_type() == "TEST_TXT"

