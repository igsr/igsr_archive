import pytest
import os
import pdb
import random
import string

from igsr_archive.file import File
from igsr_archive.db import DB
from igsr_archive.api import API

def random_generator(size=600, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

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
def load_file(rand_file):
    """
    Fixture to load a file to the RESEQTRACK DB
    """
    print('Running fixture to load test file in the DB')

    fObj = File(
        name=rand_file.name,
        type="TYPE_F")

    db.load_file(fObj, dry=False)
    print('Running fixture to load test file in the DB. DONE...')
    return rand_file.name

@pytest.fixture(scope="function")
def load_file_list(rand_filelst):
    """
    Fixture to load a list of files to the RESEQTRACK DB
    """

    print('Running fixture to load a list of test files in the DB')
    with open(rand_filelst) as f:
        for p in f:
            p = p.rstrip("\n")
            fObj = File(
                name=p,
                type="TYPE_F")
            db.load_file(fObj, dry=False)

    print('Running fixture to load a list of test files in the DB. DONE...')
    return rand_filelst

@pytest.fixture(scope="function")
def push_file(rand_file):
    """
    Fixture to push a file to FIRE. It will also load the files to the RESEQTRACK DB
    """
    print('Running fixture to push a test file to FIRE')

    fObj = File(
        name=rand_file.name,
        type="TYPE_F")

    db.load_file(fObj, dry=False)

    api.push_object(fileO=fObj,
                    fire_path="test_arch.txt",
                    dry=False)

    print('Running fixture to push a test file to FIRE. DONE...')
    return os.path.abspath(rand_file.name)

@pytest.fixture(scope="function")
def push_file_list(rand_filelst):
    """
    Fixture to push a list of files to FIRE. It will also load the files
    to the RESEQTRACK DB
    """
    print('Running fixture to push a list of test files to FIRE')
    with open(rand_filelst) as f:
        for p in f:
            p = p.rstrip("\n")
            fObj = File(
                name=p,
                type="TYPE_F")
            db.load_file(fObj, dry=False)
            basename = os.path.basename(p)
            api.push_object(fileO=fObj,
                            fire_path=basename,
                            dry=False)

    print('Running fixture to push a list of test files to FIRE. DONE...')

    return rand_filelst

@pytest.fixture(scope="function")
def delete_file():
    """
    Fixture to delete the test file from RESEQTRACK DB
    and to dearchive from FIRE
    """
    fileList = []
    yield fileList
    print('\n[teardown] delete_file finalizer, deleting file from db')
    for path in fileList:
        basename = os.path.basename(path)
        fObj = db.fetch_file(basename=basename)
        # delete from DB
        db.delete_file(fObj,
                       dry=False)
        # dearchive from FIRE
        fire_o = api.fetch_object(firePath=basename)
        api.delete_object(fireOid=fire_o.fireOid,
                          dry=False)

        print(f"[teardown] delete_file finalizer, deleting {path}")
