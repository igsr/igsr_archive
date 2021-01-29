import random
import string
import pytest
import os
import pdb

from igsr_archive.file import File
from igsr_archive.db import DB
from igsr_archive.api import API
from igsr_archive.current_tree import CurrentTree
from igsr_archive.config import CONFIG

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
    monkeypatch.setenv('SCRIPTSDIR', '../bin/')
    monkeypatch.setenv('DATADIR', '../data/')

@pytest.fixture(scope="session")
def conn_api():
    api = API(pwd=os.getenv('FIREPWD'))

    return api

@pytest.fixture(scope="function")
def rand_file():
    """
    Fixture to generate a file containing a random string

    Returns
    -------
    File that has been generated
    """
    f = open(f"{os.getenv('DATADIR')}/test_arch.txt", 'w')
    f.write(random_generator())
    f.close()

    return f

@pytest.fixture(scope="function")
def rand_filelst(dirname='../data/'):
    """
    Fixture to generate a list of files containing random strings

    Parameters
    ----------
    dirname : Directory used for putting the random files. Optional
              Default: ../data/

    Returns
    -------
    A file containing a list of file paths (one per line)
    """
    f_lst = [f"{dirname}test_arch1.txt",
             f"{dirname}test_arch2.txt",
             f"{dirname}test_arch3.txt"]

    # file with file paths
    list_f = open('../data/file_lst.txt', 'w')
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
    f_lst = ['../data/test_arch1.txt',
             '../data/test_arch2.txt',
             '../data/test_arch3.txt']

    # file with file paths
    list_f = open('../data/file_lst.txt', 'w')
    for p in f_lst:
        f = open(p, 'w')
        f.write(random_generator())
        f.close()
        fObj=File(name=f.name)
        list_f.write(f"{fObj.md5}  {p}\n")
    list_f.close()

    return list_f.name

@pytest.fixture
def ct_obj(db_obj, conn_api):
    '''
    Returns a CurrentTree object
    '''
    ct_obj = CurrentTree(db=db_obj,
                         api= conn_api,
                         staging_tree=os.getenv('DATADIR')+"/ctree/current.new.tree",
                         prod_tree=os.getenv('DATADIR')+"/ctree/current.same.tree")
    return ct_obj

@pytest.fixture
def db_dict(db_obj):
    '''
    Returns a dict from the records in DB
    '''
    fields = ['name', 'size', 'updated', 'md5']
    # limit the number of records to 10
    ctree_path, data_dict = db_obj.get_ctree(fields, outfile=os.getenv('DATADIR') + "/current.new.tree", limit=10)

    return data_dict

@pytest.fixture
def db_obj():
    """
    Fixture to get a DB object
    """

    pwd = os.getenv('DBPWD')
    dbname = os.getenv('DBNAME')

    assert dbname, "$DBNAME undefined"
    assert pwd, "$PWD undefined"

    db = DB(pwd=pwd,
            dbname=dbname)

    return db

#
# Fixtures used by test_change_events.py and test_current_tree.py
#
@pytest.fixture
def chObject_new(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a new path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "ctree/current.minus1.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture
def chObject_withdrawn(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a withdrawn path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "ctree/current.plus1.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture
def chObject_moved(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a moved path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "ctree/current.moved.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture
def chObject_replacement(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a replacement path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "ctree/current.mod.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture(scope="function")
def changelog_file():
    """
    Fixture to generate a mock CHANGELOG File object

    Returns
    -------
    File object
    """
    print('Running fixture to generate a mock CHANGELOG File object')

    mock_fpath = os.getenv('DATADIR') + "ctree/MOCK_CHANGELOG"
    f = open(mock_fpath, 'w')
    f.write("# This is a MOCK CHANGELOG file for testing purposes\n")
    f.close()
    fObj = File(
        name=mock_fpath,
        type="MOCK_CHANGELOG")

    return fObj

@pytest.fixture(scope="function")
def load_changelog_file(db_obj, changelog_file):
    """
    Fixture to load to the DB a mock CHANGELOG to be used with the CurrentTree.run function

    Returns
    -------
    File object that has been loaded to the DB
    """
    print('Running fixture to load a mock CHANGELOG file in the DB')
    db_obj.load_file(changelog_file, dry=False)
    print('Running fixture to load a mock CHANGELOG file in the DB. DONE...')

    return changelog_file

@pytest.fixture(scope="function")
def load_staging_tree(db_obj):
    """
    Fixture to load a MOCK current.tree file to DB
    """
    mock_fpath = os.getenv('DATADIR') + "ctree/current.staging.tree"
    fObj = File(
        name=mock_fpath,
        type="MOCK_CURRENT_TREE")

    db_obj.load_file(fObj, dry=False)

    return fObj

@pytest.fixture(scope="function")
def push_changelog_file(conn_api, changelog_file):
    """
    Fixture to push to the FIRE archive a mock CHANGELOG to be used with the CurrentTree.run function

    Returns
    -------
    FIRE path of the object that has been pushed
    """
    conn_api.push_object(fileO=changelog_file,
                         fire_path="ctree/MOCK_CHANGELOG",
                         dry=False)

    return "ctree/MOCK_CHANGELOG"

@pytest.fixture(scope="function")
def push_prod_tree(conn_api):
    """
    Fixture to push a mock production current.tree to the FIRE archive

    Returns
    -------
    FIRE path of the object that has been pushed
    """
    mock_fpath = os.getenv('DATADIR') + "ctree/current.minus1.tree"
    basename = os.path.basename(mock_fpath)

    fObj = File(
        name=mock_fpath,
        type="MOCK_CURRENT_TREE")

    fire_path = f"{CONFIG.get('ctree','ctree_fpath')}/{basename}"
    conn_api.push_object(fileO=fObj,
                         fire_path=fire_path,
                         dry=False)
    return fire_path

#
# Teardown fixtures
#
@pytest.fixture(scope="function")
def del_from_db(db_obj) :
    """
    Fixture to delete file/s from the DB
    """
    fileList = []
    yield fileList
    print('\n[teardown] del_from_db finalizer, deleting from DB')
    for path in fileList:
        basename = os.path.basename(path)
        fObj = db_obj.fetch_file(basename=basename)
        # delete from DB
        db_obj.delete_file(fObj,
                           dry=False)
    print(f"[teardown] del_from_db finalizer, deleting object with path: {path}")

@pytest.fixture(scope="function")
def dearchive_file(db_obj, conn_api) :
    """
    Fixture to dearchive files from FIRE
    """
    pathList = []
    yield pathList
    print('\n[teardown] dearchive_file finalizer, dearchiving from FIRE')
    for path in pathList:
        # dearchive from FIRE
        fire_o = conn_api.fetch_object(firePath=path)
        conn_api.delete_object(fireOid=fire_o.fireOid,
                               dry=False)

        print(f"[teardown] dearchive_file finalizer, deleting object with firePath: {path}")
