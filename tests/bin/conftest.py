import pytest
import os
import random
import string

from configparser import ConfigParser

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

@pytest.fixture(scope="session")
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

def rand_filelst():
    """
    Fixture to generate a list of files containing random strings

    Returns
    -------
    A file containing a list of file paths (one per line)
    """