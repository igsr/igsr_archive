import pytest
import os
import pdb
import random
import string

from configparser import ConfigParser
from igsr_archive.file import File

def random_generator(size=600, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@pytest.fixture(scope="session")
def modify_settings(request):
    """
    Fixture to modify the settings.ini
    and generate a modified version that will be used
    in this file
    """
    # modify current settings.ini
    parser = ConfigParser()
    parser.read('../../data/settings.ini')
    abs_dir = os.path.abspath('../../data/')
    parser.set('ftp', 'staging_mount', abs_dir)

    with open('../../data/settings_m.ini', 'w') as configfile:
        parser.write(configfile)

    def fin():
        print('\n[teardown] modify_settings finalizer, deleting modified settings file')
        os.remove('../../data/settings_m.ini')

    request.addfinalizer(fin)

    return '../../data/settings_m.ini'

@pytest.fixture(scope="function")
def rand_file():
    """
    Fixture to generate a file containing a random string

    Returns
    -------
    File that has been generated
    """
    f = open('../../data/test_arch.txt', 'w')
    f.write(random_generator())
    f.close()

    return f

@pytest.fixture(scope="session")
def rand_filelst():
    """
    Fixture to generate a list of files containing random strings

    Returns
    -------
    A file containing a list of file paths (one per line)
    """
    f_lst = ['../../data/test_arch1.txt',
             '../../data/test_arch2.txt',
             '../../data/test_arch3.txt']

    # file with file paths
    list_f = open('../../data/file_lst.txt', 'w')
    for p in f_lst:
        list_f.write(p+"\n")
        f = open(p, 'w')
        f.write(random_generator())
        f.close()
    list_f.close()

    return list_f.name

@pytest.fixture(scope="session")
def rand_filelst_md5():
    """
    Fixture to generate a list of files containing random strings
    It will save the file paths in the format:
    <md5sum>  <path>

    Returns
    -------
    A file containing a list of file paths (one per line)
    """
    f_lst = ['../../data/test_arch1.txt',
             '../../data/test_arch2.txt',
             '../../data/test_arch3.txt']

    # file with file paths
    list_f = open('../../data/file_lst.txt', 'w')
    for p in f_lst:
        f = open(p, 'w')
        f.write(random_generator())
        f.close()
        fObj=File(name=f.name)
        list_f.write(f"{fObj.md5}  {p}\n")
    list_f.close()

    return list_f.name

@pytest.fixture(scope="function")
def load_file():
    """
    Fixture to load a file in a RESEQTRACK DB
    """