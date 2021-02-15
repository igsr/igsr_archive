import pytest
import os
import pdb
import random
import string

from igsr_archive.file import File

def random_generator(size=600, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """
    Defining the environment
    """
    assert os.getenv('DBNAME'), "$DBNAME undefined. You need to test this env variable to run the tests"
    assert os.getenv('DBPWD'), "$DBPWD undefined. You need to test this env variable to run the tests"
    assert os.getenv('FIREPWD'), "$FIREPWD undefined. You need to test this env variable to run the tests"
    monkeypatch.setenv('SCRIPTSDIR', os.path.abspath('../../bin/'))
    monkeypatch.setenv('DATADIR',  os.path.abspath('../../data/'))

@pytest.fixture(scope="function")
def load_file(rand_file, db_obj):
    """
    Fixture to load a file to the RESEQTRACK DB
    """
    print('Running fixture to load test file in the DB')
    fObj = File(
        name=rand_file.name,
        type="TYPE_F")

    db_obj.load_file(fObj, dry=False)
    print('Running fixture to load test file in the DB. DONE...')
    return rand_file.name

@pytest.fixture(scope="function")
def load_file_list(rand_filelst, db_obj):
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
            db_obj.load_file(fObj, dry=False)

    print('Running fixture to load a list of test files in the DB. DONE...')
    return rand_filelst

@pytest.fixture(scope="function")
def push_file(rand_file, db_obj, conn_api):
    """
    Fixture to push a file to FIRE. It will also load the files to the RESEQTRACK DB
    """
    print('Running fixture to push a test file to FIRE')

    fObj = File(
        name=rand_file.name,
        type="TYPE_F")

    db_obj.load_file(fObj, dry=False)

    conn_api.push_object(fileO=fObj,
                         fire_path="test_arch.txt",
                         dry=False)

    print('Running fixture to push a test file to FIRE. DONE...')
    return os.path.abspath(rand_file.name)

@pytest.fixture(scope="function")
def push_file_list(rand_filelst, db_obj, conn_api):
    """
    Fixture to push a list of files to FIRE. It will also load the files
    to the RESEQTRACK DB

    Returns
    -------
    File with the lisf of file paths that have been pushed
    """
    print('Running fixture to push a list of test files to FIRE')
    with open(rand_filelst) as f:
        for p in f:
            p = p.rstrip("\n")
            fObj = File(
                name=p,
                type="TYPE_F")
            db_obj.load_file(fObj, dry=False)
            basename = os.path.basename(p)
            conn_api.push_object(fileO=fObj,
                                 fire_path=basename,
                                 dry=False)

    print('Running fixture to push a list of test files to FIRE. DONE...')

    return rand_filelst

@pytest.fixture(scope="function")
def delete_file(db_obj, conn_api) :
    """
    Fixture to delete the test file from RESEQTRACK DB
    and to dearchive from FIRE
    """
    fileList = []
    yield fileList
    print('\n[teardown] delete_file finalizer, deleting file from db')
    for path in fileList:
        basename = os.path.basename(path)
        fObj = db_obj.fetch_file(basename=basename)
        # delete from DB
        db_obj.delete_file(fObj,
                            dry=False)
        # dearchive from FIRE
        fire_o = conn_api.fetch_object(firePath=basename)
        conn_api.delete_object(fireOid=fire_o.fireOid,
                               dry=False)

        print(f"[teardown] delete_file finalizer, deleting {path}")
