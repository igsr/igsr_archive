import pytest
import os
import pdb
import random
import string
import subprocess
from configparser import ConfigParser
from igsr_archive.db import DB
from igsr_archive.api import API
from igsr_archive.file import File

# get password-related info from environment
fpwd = os.getenv('FIREPWD')
dbpwd = os.getenv('DBPWD')
dbname = os.getenv('DBNAME')
assert fpwd, "$FIREPWD undefined"
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

def random_generator(size=600, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@pytest.fixture(scope="module")
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

@pytest.fixture
def load_file(request):
    """
    Fixture to load a file to the RESEQTRACK DB and to delete
    the pushed file from FIRE
    """
    print('Running fixture to load test file in the DB')

    db = DB(settingsf="../../data/settings.ini",
            pwd=dbpwd,
            dbname=dbname)

    f = open('../../data/test_arch.txt', 'w')
    f.write(random_generator())
    f.close()

    fObj = File(
        name=f.name,
        type="TYPE_F")

    db.load_file(fObj, dry=False)
    def fin():
        print('\n[teardown] load_file finalizer, deleting file from db and dearchiving file from FIRE')
        api = API(settingsf="../../data/settings.ini",
                  pwd=fpwd)
        basename = os.path.basename(f.name)
        fire_o = api.fetch_object(firePath=basename)
        api.delete_object(fireOid=fire_o.fireOid,
                          dry=False)

        arch_obj = db.fetch_file(basename=basename)
        db.delete_file(arch_obj,
                       dry=False)
    request.addfinalizer(fin)
    print('Running fixture to load test file in the DB. DONE...')

    return f.name

@pytest.fixture
def load_file_list(request):
    """
    Fixture to load a list of files to the RESEQTRACK DB and to delete the pushed files
    from FIRE
    """

    print('Running fixture to load a list of test files in the DB')

    db = DB(settingsf="../../data/settings.ini",
            pwd=dbpwd,
            dbname=dbname)

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
        fObj = File(
            name=f.name,
            type="TYPE_F")
        db.load_file(fObj, dry=False)
    list_f.close()

    def fin():
        print('\n[teardown] load_file_list finalizer, deleting list of files from db and dearchiving from FIRE')
        api = API(settingsf="../../data/settings.ini",
                  pwd=fpwd)
        for p in f_lst:
            basename = os.path.basename(p)
            fire_o = api.fetch_object(firePath=basename)
            api.delete_object(fireOid=fire_o.fireOid,
                              dry=False)
            arch_obj = db.fetch_file(basename=basename)
            db.delete_file(arch_obj,
                           dry=False)
        print('\n[teardown] load_file_list finalizer, deleting ../../data/file_lst.txt')
        os.remove('../../data/file_lst.txt')
    request.addfinalizer(fin)
    print('Running fixture to load a list of test files in the DB. DONE...')

    return list_f.name

def test_single_file(modify_settings, load_file):

    print('Archive a single file using -f and --dry False options')

    cmd = f"../../bin/archive_files.py -f {load_file} --dry False --settings {modify_settings}" \
          f" --dbname {dbname} --dbpwd {dbpwd} --firepwd {fpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")

    print('Archive a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_file_list(modify_settings, load_file_list):

    print('Archive a list of files using -l and --dry False options')

    cmd = f"../../bin/archive_files.py -l {load_file_list} --dry False --settings {modify_settings}" \
          f" --dbname {dbname} --dbpwd {dbpwd} --firepwd {fpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")

    print('Archive a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0