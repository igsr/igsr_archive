import pytest
import os
import pdb
import subprocess
from igsr_archive.db import DB
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
    parser.set('ftp', 'ftp_mount', abs_dir)

    with open('../../data/settings_m.ini', 'w') as configfile:
        parser.write(configfile)

    def fin():
        print('\n[teardown] modify_settings finalizer, deleting modified settings file')
        os.remove('../../data/settings_m.ini')

    request.addfinalizer(fin)

    return '../../data/settings_m.ini'

def test_single_file(push_file, modify_settings):

    print('Dearchive a single file using -f and --dry False options')

    cmd = f"../../bin/dearchive_files.py -f {push_file} --dry False -d ../../data/ --settings {modify_settings}" \
          f" --dbname {dbname} --dbpwd {dbpwd} --firepwd {fpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong. STDERR:##\n: {stderr}\n##")
        print(f"\n##Something went wrong. STDOUT:##\n: {stdout}\n##")

    # delete dearchived file
    os.remove('../../data/test_arch.txt')

def test_file_list(push_file_list, modify_settings):

    print('Dearchive a list of files using -l and --dry False options')

    cmd = f"../../bin/dearchive_files.py -l {push_file_list} --dry False -d ../../data/ --settings {modify_settings}" \
          f" --dbname {dbname} --dbpwd {dbpwd} --firepwd {fpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")
    stdout = stdout.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong. STDERR:##\n: {stderr}\n##")
        print(f"\n##Something went wrong. STDOUT:##\n: {stdout}\n##")

    # deleting test files
    with open(push_file_list) as f:
        for path in f:
            path = path.rstrip("\n")
            os.remove(path)
    os.remove(push_file_list)