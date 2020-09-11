import pytest
import os
import pdb
import subprocess

@pytest.fixture
def delete_file(conn_db):
    """
    Fixture to delete a file from the RESEQTRACK DB
    It will also delete the file
    """
    fileList = []
    yield fileList
    print('\n[teardown] delete_file finalizer, deleting file from db')

    for path in fileList:
        fObj = conn_db.fetch_file(path=path)
        conn_db.delete_file(fObj,
                       dry=False)
        print(f"[teardown] delete_file finalizer, deleting {path}")
        os.remove(path)

def test_single_file(settings_f, rand_file, delete_file):

    print('Load a single file using -f and --dry False options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/load_files.py -f {rand_file.name} --dry False --settings {settings_f}" \
          f" --dbname {os.getenv('DBNAME')} --pwd {os.getenv('DBPWD')}"

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

    delete_file.append(rand_file.name)

    print('Load a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_single_file_w_type(conn_db, settings_f, rand_file, delete_file):

    print('Load a single file using -f, --type TEST_TYPE and --dry False options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/load_files.py -f {rand_file.name} --dry False --settings {settings_f}" \
          f" --dbname {os.getenv('DBNAME')} --type TEST_TYPE --pwd {os.getenv('DBPWD')}"

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

    assert ret.returncode == 0

    print('Load a single file using -f, --type TEST_TYPE and --dry False options. DONE...')
    print('Checking that stored file has the right file type=TEST_TYPE')
    fetched_F = conn_db.fetch_file(path=rand_file.name)
    assert fetched_F.type == 'TEST_TYPE'
    print('Checking that stored file has the right file type=TEST_TYPE. DONE...')

    delete_file.append(rand_file.name)

def test_file_list(rand_filelst, settings_f, delete_file):

    print('Load a list of files using -l and --dry False options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/load_files.py -l {rand_filelst} --dry False --settings {settings_f}" \
          f" --dbname {os.getenv('DBNAME')} --pwd {os.getenv('DBPWD')}"

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
    with open(rand_filelst) as f:
        for path in f:
            path = path.rstrip("\n")
            delete_file.append(path)
    os.remove(rand_filelst)
    print('Load a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0

def test_w_md5_file(rand_filelst_md5, settings_f, delete_file):
    print('Load a single file using --md5_file and --dry False options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/load_files.py --md5_file {rand_filelst_md5} --dry False --settings {settings_f}" \
          f" --dbname {os.getenv('DBNAME')} --pwd {os.getenv('DBPWD')}"

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

    # deleting test files
    with open(rand_filelst_md5) as f:
        for line in f:
            line = line.rstrip("\n")
            path = line.split("  ")[1]
            delete_file.append(path)
    os.remove(rand_filelst_md5)
    print('Load a single file using --md5_file and --dry False options. DONE...')

