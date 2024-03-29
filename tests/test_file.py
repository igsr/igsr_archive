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

    assert f.md5 == "0b1578b3dbfca89caa03a88949d68fa4"

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

    assert f.size == 8

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

def test_guess_type():
    log = logging.getLogger('test_guess_type')
    log.debug('Testing function for guess the type of a file')

    f = File(name=f"{os.getenv('DATADIR')}/test.txt")

    assert f.guess_type() == "TXT"

def test_guess_type1(rand_file):
    log = logging.getLogger('test_guess_type1')
    log.debug('Testing function for guess the type of a complex filename')
    new_fname = f"{os.getenv('DATADIR')}/test_arch.2020.txt"
    # change the basename to something more complex
    os.rename(f"{os.getenv('DATADIR')}/test_arch.txt", new_fname)
    f = File(name=new_fname)

    # delete test type
    os.remove(new_fname)
    assert f.guess_type() == "TXT"

def test_guess_type_default():
    log = logging.getLogger('test_guess_type_default')
    log.debug('Testing function to check when a default '
              'type is assigned when the extension is'
              'not recognised')

    new_fname = f"{os.getenv('DATADIR')}/test.2020.pippo"
    f = File(name=new_fname)

    assert f.guess_type() == "MISC"

