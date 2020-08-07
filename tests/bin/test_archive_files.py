import pytest
import os
import logging
import subprocess
from configparser import ConfigParser

# get password-related info from environment
fpwd = os.getenv('FIREPWD')
dbpwd = os.getenv('DBPWD')
dbname = os.getenv('DBNAME')
assert fpwd, "$FIREPWD undefined"
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

def modify_settings(s):
    """
    Function to modify the settings.ini
    file
    """
    # modify current settings.ini
    parser = ConfigParser()
    parser.read(s)
    parser.set('ftp', 'staging_mount', '../../data/')

    with open('../../data/settings_m.ini', 'w') as configfile:
        parser.write(configfile)

def test_single_file_dry():
    log = logging.getLogger('dry test_functionality_with_single_file')

    log.debug('Archive a single file using -f and --dry True options')

    modify_settings('../../data/prod_settings.ini')

    subprocess.Popen(['../../bin/archive_files.py',
                      '-f', '../../data/test.txt',
                      '--dry', 'True',
                      '--settings', '../../data/prod_settings.ini',
                      '--dbname', dbname,
                      '--dbpwd', dbpwd,
                      '--firepwd', fpwd])

    assert 0