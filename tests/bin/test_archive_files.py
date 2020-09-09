import pytest
import os
import pdb
import subprocess
from igsr_archive.db import DB
from igsr_archive.api import API
from configparser import ConfigParser

# get password-related info from environment
fpwd = os.getenv('FIREPWD')
dbpwd = os.getenv('DBPWD')
dbname = os.getenv('DBNAME')
assert fpwd, "$FIREPWD undefined"
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

db = DB(settingsf="../../data/settings.ini",
        pwd=dbpwd,
        dbname=dbname)

api = API(settingsf="../../data/settings.ini",
          pwd=fpwd)

@pytest.fixture
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

def test_single_file(modify_settings, load_file, delete_file):

    print('Archive a single file using -f and --dry False options')

    cmd = f"../../bin/archive_files.py -f {load_file} --dry False --settings {modify_settings}" \
          f" --dbname {dbname} --dbpwd {dbpwd} --firepwd {fpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")
        print(f"\n##Something went wrong. STDOUT:##\n: {stdout}\n##")

    delete_file.append(load_file)

    print('Archive a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_file_list(modify_settings, load_file_list, delete_file):

    print('Archive a list of files using -l and --dry False options')

    cmd = f"../../bin/archive_files.py -l {load_file_list} --dry False --settings {modify_settings}" \
          f" --dbname {dbname} --dbpwd {dbpwd} --firepwd {fpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")
        print(f"\n##Something went wrong. STDOUT:##\n: {stdout}\n##")

    # deleting test files
    with open(load_file_list) as f:
        for path in f:
            path = path.rstrip("\n")
            delete_file.append(path)
    os.remove(load_file_list)

    print('Archive a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0