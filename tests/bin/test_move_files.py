import pytest
import os
import pdb
import subprocess
import re

from igsr_archive.config import CONFIG

@pytest.fixture(scope="function")
def modify_settings(request):
    """
    Fixture to modify the settings.ini
    and generate a modified version that will be used
    in this file
    """

    abs_dir = os.path.abspath(os.getenv('DATADIR'))
    CONFIG.set('ftp', 'ftp_mount', abs_dir)

    with open('settings_m.ini', 'w') as configfile:
        CONFIG.write(configfile)

    def fin():
        print('\n[teardown] modify_settings finalizer, deleting modified settings file')
        os.remove('settings_m.ini')

    request.addfinalizer(fin)

    return 'settings_m.ini'

@pytest.fixture
def delete_arch_file(modify_settings, conn_db, conn_api):
    """
    Fixture to delete the moved test file/s
    from DB and to dearchive it from FIRE
    """
    fileList = []
    yield fileList
    print('\n[teardown] delete_arch_file finalizer, deleting file from db')

    CONFIG.read(modify_settings)

    for path in fileList:
        basename = os.path.basename(path)
        fObj = conn_db.fetch_file(basename=basename)
        # delete from DB
        conn_db.delete_file(fObj,
                            dry=False)
        # dearchive from FIRE
        fire_path =  re.sub(CONFIG.get('ftp', 'ftp_mount') + "/", '', path)
        fire_o = conn_api.fetch_object(firePath=fire_path)
        conn_api.delete_object(fireOid=fire_o.fireOid,
                               dry=False)

        print(f"[teardown] delete_arch_file finalizer, deleting {path}")

def test_single_file(push_file, modify_settings, delete_arch_file):

    print('Move a single file using -f and --dry False options')

    dest_path = os.path.abspath('../../data/out/test_arch.txt')

    cmd = f"{os.getenv('SCRIPTSDIR')}/move_files.py --origin {push_file} --dest {dest_path} --dry False --settings {modify_settings}" \
          f" --dbname {os.getenv('DBNAME')} --dbpwd {os.getenv('DBPWD')} --firepwd {os.getenv('FIREPWD')}"

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

    delete_arch_file.append(dest_path)
    os.remove(push_file)

    print('Move a single file using -f and --dry False options. DONE...')
    assert ret.returncode == 0

def test_file_list(push_file_list, modify_settings, delete_arch_file):

    print('Move a list of files using -l and --dry False options')
    list_f = open(f"{os.getenv('DATADIR')}/move_lst.txt", 'w')
    with open(push_file_list) as f:
        for path in f:
            path = path.rstrip("\n")
            origin_p = os.path.abspath(path)
            dest_p = os.path.abspath(f"{os.getenv('DATADIR')}/out/"+os.path.basename(path))
            list_f.write(origin_p+"\t"+dest_p+"\n")
    list_f.close()

    cmd = f"{os.getenv('SCRIPTSDIR')}/move_files.py -l {list_f.name} --dry False --settings {modify_settings}" \
          f" --dbname {os.getenv('DBNAME')} --dbpwd {os.getenv('DBPWD')} --firepwd {os.getenv('FIREPWD')}"

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

    # now, delete test files
    with open(list_f.name) as f:
        for line in f:
            origin_path = line.split("\t")[0]
            os.remove(origin_path)
            dest_path = line.split("\t")[1].rstrip("\n")
            delete_arch_file.append(dest_path)
    os.remove(list_f.name)
    os.remove(push_file_list)

    print('Move a list of files using -l and --dry False options. DONE...')
    assert ret.returncode == 0

def test_move_dir(push_file_list, modify_settings, delete_arch_file):

    print('Move the files in a directory using the --src_dir and --tg_dir options')

    cmd = f"{os.getenv('SCRIPTSDIR')}/move_files.py --src_dir \"{os.getenv('DATADIR')}/test_arch*.txt\" --tg_dir {os.getenv('DATADIR')}/out/ --dry False --settings {modify_settings}" \
          f" --dbname {os.getenv('DBNAME')} --dbpwd {os.getenv('DBPWD')} --firepwd {os.getenv('FIREPWD')}"

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

    # remove newly created files
    with open(push_file_list) as f:
        for path in f:
            path = path.rstrip("\n")
            dest_p = os.path.abspath(f"{os.getenv('DATADIR')}/out/"+os.path.basename(path))
            os.remove(path)
            delete_arch_file.append(dest_p)

    os.remove(push_file_list)
