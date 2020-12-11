import random
import string
import pytest
import os

from igsr_archive.file import File
from igsr_archive.db import DB
from igsr_archive.api import API

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

@pytest.fixture(scope="session")
def conn_db():
    db = DB(pwd=os.getenv('DBPWD'),
            dbname=os.getenv('DBNAME'))
    return db

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