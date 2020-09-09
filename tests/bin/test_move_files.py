import pytest
import os
import pdb
import subprocess
import re

from configparser import ConfigParser
from igsr_archive.db import DB
from igsr_archive.api import API

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
    parser.set('ftp', 'ftp_mount', abs_dir)

    with open('../../data/settings_m.ini', 'w') as configfile:
        parser.write(configfile)

    def fin():
        print('\n[teardown] modify_settings finalizer, deleting modified settings file')
        os.remove('../../data/settings_m.ini')

    request.addfinalizer(fin)

    return '../../data/settings_m.ini'

@pytest.fixture
def delete_arch_file(modify_settings):
    """
    Fixture to delete the moved test file/s
    from DB and to dearchive it from FIRE
    """
    fileList = []
    yield fileList
    print('\n[teardown] delete_arch_file finalizer, deleting file from db')
    parser = ConfigParser()
    parser.read(modify_settings)

    for path in fileList:
        basename = os.path.basename(path)
        fObj = db.fetch_file(basename=basename)
        # delete from DB
        db.delete_file(fObj,
                       dry=False)
        # dearchive from FIRE
        fire_path =  re.sub(parser.get('ftp', 'ftp_mount') + "/", '', path)
        fire_o = api.fetch_object(firePath=fire_path)
        api.delete_object(fireOid=fire_o.fireOid,
                          dry=False)

        print(f"[teardown] delete_arch_file finalizer, deleting {path}")

def test_single_file(push_file, modify_settings, delete_arch_file):

    print('Move a single file using -f and --dry False options')

    dest_path = os.path.abspath('../../data/out/test_arch.txt')

    cmd = f"../../bin/move_files.py --origin {push_file} --dest {dest_path} --dry False --settings {modify_settings}" \
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

    delete_arch_file.append(dest_path)
    os.remove(push_file)

    print('Move a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_file_list(push_file_list, modify_settings, delete_arch_file):

    print('Move a list of files using -l and --dry False options')
    list_f = open('../../data/move_lst.txt', 'w')
    with open(push_file_list) as f:
        for path in f:
            path = path.rstrip("\n")
            origin_p = os.path.abspath(path)
            dest_p = os.path.abspath('../../data/out/'+os.path.basename(path))
            list_f.write(origin_p+"\t"+dest_p+"\n")
    list_f.close()

    cmd = f"../../bin/move_files.py -l {list_f.name} --dry False --settings {modify_settings}" \
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

    # now, delete test files
    with open(list_f.name) as f:
        for line in f:
            origin_path = line.split("\t")[0]
            os.remove(origin_path)
            dest_path = line.split("\t")[1].rstrip("\n")
            delete_arch_file.append(dest_path)
    os.remove(list_f.name)
    os.remove(push_file_list)

    print('Move a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0