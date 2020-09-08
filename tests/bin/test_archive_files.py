import pytest
import os
import pdb
import subprocess
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

db = DB(settingsf="../../data/settings.ini",
        pwd=dbpwd,
        dbname=dbname)

@pytest.fixture
def load_file(request, rand_file):
    """
    Fixture to load a file to the RESEQTRACK DB and to delete
    the pushed file from FIRE
    """
    print('Running fixture to load test file in the DB')

    fObj = File(
        name=rand_file.name,
        type="TYPE_F")

    db.load_file(fObj, dry=False)
    def fin():
        print('\n[teardown] load_file finalizer, deleting file from db and dearchiving file from FIRE')
        api = API(settingsf="../../data/settings.ini",
                  pwd=fpwd)
        basename = os.path.basename(rand_file.name)
        fire_o = api.fetch_object(firePath=basename)
        api.delete_object(fireOid=fire_o.fireOid,
                          dry=False)

        arch_obj = db.fetch_file(basename=basename)
        db.delete_file(arch_obj,
                       dry=False)
    request.addfinalizer(fin)
    print('Running fixture to load test file in the DB. DONE...')

    return rand_file.name

@pytest.fixture
def load_file_list(request, rand_filelst):
    """
    Fixture to load a list of files to the RESEQTRACK DB and to delete the pushed files
    from FIRE
    """

    print('Running fixture to load a list of test files in the DB')

    with open(rand_filelst) as f:
        for p in f:
            p = p.rstrip("\n")
            fObj = File(
                name=p,
                type="TYPE_F")
            db.load_file(fObj, dry=False)

    def fin():
        pdb.set_trace()
        print('\n[teardown] load_file_list finalizer, deleting list of files from db and dearchiving from FIRE')
        api = API(settingsf="../../data/settings.ini",
                  pwd=fpwd)
        with open(rand_filelst) as f:
            for p in f:
                p = p.rstrip("\n")
                basename = os.path.basename(p)
                fire_o = api.fetch_object(firePath=basename)
                api.delete_object(fireOid=fire_o.fireOid,
                                  dry=False)
                arch_obj = db.fetch_file(basename=basename)
                db.delete_file(arch_obj,
                               dry=False)
        print('[teardown] load_file_list finalizer, deleting ../../data/file_lst.txt')
        os.remove('../../data/file_lst.txt')
    request.addfinalizer(fin)
    print('Running fixture to load a list of test files in the DB. DONE...')

    return rand_filelst

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