import pytest
import os
import pdb
import random
import string
import subprocess
from configparser import ConfigParser
from igsr_archive.db import DB
from igsr_archive.file import File

# get password-related info from environment
dbpwd = os.getenv('DBPWD')
dbname = os.getenv('DBNAME')
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

def random_generator(size=600, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

db = DB(settingsf="../../data/settings.ini",
        pwd=dbpwd,
        dbname=dbname)

@pytest.fixture
def load_file(request):
    """
    Fixture to load a file to the RESEQTRACK DB
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
    print('Running fixture to load test file in the DB. DONE...')

    def fin():
        print('\n[teardown] load_file finalizer, deleting unnecessary files')
        os.remove('../../data/test_arch.txt')

    request.addfinalizer(fin)

    return f.name

@pytest.fixture
def load_file_list(request):
    """
    Fixture to load a list of files to the RESEQTRACK DB
    """

    print('Running fixture to load a list of test files in the DB')

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
        print('\n[teardown] load_file_list finalizer, deleting unnecessary files')
        for p in f_lst:
            os.remove(p)
        os.remove('../../data/file_lst.txt')
    request.addfinalizer(fin)
    print('Running fixture to load a list of test files in the DB. DONE...')

    return list_f.name

def test_single_file(load_file):

    print('Delete a single file using -f and --dry False options')

    cmd = f"../../bin/delete_files.py -f {load_file} --dry False --settings ../../data/settings.ini" \
          f" --dbname {dbname} --pwd {dbpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")

    print('Delete a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_file_list(load_file_list):

    print('Delete a list of files using -l and --dry False options')

    cmd = f"../../bin/delete_files.py -l {load_file_list} --dry False --settings ../../data/settings.ini" \
          f" --dbname {dbname} --pwd {dbpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")

    print('Delete a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0