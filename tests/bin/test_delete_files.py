import pytest
import os
import pdb
import subprocess
from igsr_archive.file import File
from igsr_archive.db import DB

# get password-related info from environment
dbpwd = os.getenv('DBPWD')
dbname = os.getenv('DBNAME')
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

db = DB(settingsf="../../data/settings.ini",
        pwd=dbpwd,
        dbname=dbname)

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
    stdout = stdout.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong. STDERR:##\n: {stderr}\n##")
        print(f"\n##Something went wrong. STDOUT:##\n: {stdout}\n##")

    # delete test file
    os.remove(load_file)

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
    stdout = stdout.decode("utf-8")

    if ret.returncode != 0:
        print(f"\n##Something went wrong. STDERR:##\n: {stderr}\n##")
        print(f"\n##Something went wrong. STDOUT:##\n: {stdout}\n##")

    # deleting test files
    with open(load_file_list) as f:
        for path in f:
            path=path.rstrip("\n")
            os.remove(path)
    os.remove(load_file_list)

    print('Delete a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0