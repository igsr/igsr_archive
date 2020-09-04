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
def generate_file(request):
    """
    Fixture to generate a test file that will be loaded to the RESEQTRACK DB
    """
    print('Running fixture to generate a test file')

    f = open('../../data/test_arch.txt', 'w')
    f.write(random_generator())
    f.close()

    def fin():
        print('\n[teardown] generate_file finalizer, deleting file from db')
        fObj = db.fetch_file(path=f.name)
        db.delete_file(fObj,
                       dry=False)
        print('[teardown] generate_file finalizer, deleting ../../data/test_arch.txt')
        os.remove('../../data/test_arch.txt')
    request.addfinalizer(fin)
    return f.name

@pytest.fixture
def generate_file_list(request):
    """
    Fixture to generate a list of test files, that will be loaded in the
    RESEQTRACK database
    """

    print('Running fixture to generate a list of test files')

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

    def fin():
        print('\n[teardown] generate_file_list finalizer, deleting list of files from db')
        for p in f_lst:
            arch_obj = db.fetch_file(path=p)
            db.delete_file(arch_obj,
                           dry=False)
            os.remove(p)
        print('[teardown] generate_file_list finalizer, deleting unnecessary files')
        os.remove('../../data/file_lst.txt')

    request.addfinalizer(fin)

    return list_f.name

@pytest.fixture
def generate_md5_flist(request):
    """
    Fixture to generate a file containing a list of file paths along with their MD5SUMs
    These files will be loaded in the RESEQTRACK DB
    """

    print('Running fixture to generate a list of test files along with their MD5SUMs')

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

    def fin():
        print('\n[teardown] generate_md5_flist finalizer, deleting list of files from db')
        for p in f_lst:
            arch_obj = db.fetch_file(path=p)
            db.delete_file(arch_obj,
                           dry=False)
            os.remove(p)
        print('[teardown] generate_file_list finalizer, deleting unnecessary files')
        os.remove('../../data/file_lst.txt')

    request.addfinalizer(fin)

    return list_f.name

def test_single_file(generate_file):

    print('Load a single file using -f and --dry False options')

    cmd = f"../../bin/load_files.py -f {generate_file} --dry False --settings ../../data/settings.ini" \
          f" --dbname {dbname} --pwd {dbpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")

    print('Load a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_single_file_w_type(generate_file):

    print('Load a single file using -f, --type TEST_TYPE and --dry False options')
    cmd = f"../../bin/load_files.py -f {generate_file} --dry False --settings ../../data/settings.ini" \
          f" --dbname {dbname} --type TEST_TYPE --pwd {dbpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")
    assert ret.returncode == 0

    print('Load a single file using -f, --type TEST_TYPE and --dry False options. DONE...')
    print('Checking that stored file has the right file type=TEST_TYPE')
    fetched_F = db.fetch_file(path=generate_file)
    assert fetched_F.type == 'TEST_TYPE'
    print('Checking that stored file has the right file type=TEST_TYPE. DONE...')

def test_file_list(generate_file_list):

    print('Load a list of files using -l and --dry False options')

    cmd = f"../../bin/load_files.py -l {generate_file_list} --dry False --settings ../../data/settings.ini" \
          f" --dbname {dbname} --pwd {dbpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")

    print('Load a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0

def test_w_md5_file(generate_md5_flist):
    print('Load a single file using --md5_file and --dry False options')

    cmd = f"../../bin/load_files.py --md5_file {generate_md5_flist} --dry False --settings ../../data/settings.ini" \
          f" --dbname {dbname} --pwd {dbpwd}"

    ret = subprocess.Popen(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = ret.communicate()

    stderr = stderr.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong##\n: {stderr}\n##")
    print('Load a single file using --md5_file and --dry False options. DONE...')

