import pytest
import os
import pdb
import subprocess
from configparser import ConfigParser

@pytest.fixture
def modify_settings(request, settings_f):
    """
    Fixture to modify the settings.ini
    and generate a modified version that will be used
    in this file
    """
    # modify current settings.ini
    parser = ConfigParser()
    parser.read(settings_f)
    abs_dir = os.path.abspath(os.getenv('DATADIR'))
    parser.set('ftp', 'ftp_mount', abs_dir)

    with open('settings_m.ini', 'w') as configfile:
        parser.write(configfile)

    def fin():
        print('\n[teardown] modify_settings finalizer, deleting modified settings file')
        os.remove('settings_m.ini')

    request.addfinalizer(fin)

    return 'settings_m.ini'

def test_single_file(push_file, modify_settings):

    print('Dearchive a single file using -f and --dry False options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/dearchive_files.py -f {push_file} --dry False -d {os.getenv('DATADIR')} --settings {modify_settings}" \
          f" --dbname {os.getenv('DBNAME')} --dbpwd {os.getenv('DBPWD')} --firepwd {os.getenv('FIREPWD')}"

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
    os.remove(f"{os.getenv('DATADIR')}/test_arch.txt")

def test_file_list(push_file_list, modify_settings):

    print('Dearchive a list of files using -l and --dry False options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/dearchive_files.py -l {push_file_list} --dry False -d {os.getenv('DATADIR')} --settings {modify_settings}" \
          f" --dbname {os.getenv('DBNAME')} --dbpwd {os.getenv('DBPWD')} --firepwd {os.getenv('FIREPWD')}"

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