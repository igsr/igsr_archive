import pytest
import logging
import os
import glob
import pdb
import re

from igsr_archive.config import CONFIG

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def clean_tmp():
    yield
    log = logging.getLogger('clean_tmp')
    log.debug('Cleaning tmp files')

    files = glob.glob(os.getenv('DATADIR')+'/ctree/changelog_details_*')
    for f in files:
        os.remove(f)

    # delete CHANGELOG file
    files1 = glob.glob(os.getenv('DATADIR')+'/ctree/MOCK_CHANGELOG*')
    for f in files1:
        os.remove(f)

def test_print_chlog_details_new(chObject_new, clean_tmp):
    log = logging.getLogger('test_print_chlog_details_new')

    log.debug('Testing the \'print_chlog_details\' function to '
              'generate a changelog_details_*_new file')

    ofiles = chObject_new.print_chlog_details(os.getenv('DATADIR')+'/ctree')

    p = re.compile('.*_new$')
    m = p.match(ofiles[0])
    m_seen = False
    if m:
        m_seen = True

    # check that the single path in the list exists
    assert os.path.exists(ofiles[0]) == 1
    assert m_seen is True

def test_print_chlog_details_withdrawn(chObject_withdrawn, clean_tmp):
    log = logging.getLogger('test_print_chlog_details_withdrawn')

    log.debug('Testing the \'print_chlog_details\' function to '
              'generate a changelog_details_*_withdrawn file')

    ofiles = chObject_withdrawn.print_chlog_details(os.getenv('DATADIR')+'/ctree')

    p = re.compile('.*_withdrawn$')
    m = p.match(ofiles[0])
    m_seen = False
    if m:
        m_seen = True

    # check that the single path in the list exists
    assert os.path.exists(ofiles[0]) == 1
    assert m_seen is True

def test_print_chlog_details_moved(chObject_moved, clean_tmp):
    log = logging.getLogger('test_print_chlog_details_moved')

    log.debug('Testing the \'print_chlog_details\' function to '
              'generate a changelog_details_*_moved file')

    ofiles = chObject_moved.print_chlog_details(os.getenv('DATADIR')+'/ctree')

    p = re.compile('.*_moved$')
    m = p.match(ofiles[0])
    m_seen = False
    if m:
        m_seen = True

    # check that the single path in the list exists
    assert os.path.exists(ofiles[0]) == 1
    assert m_seen is True

def test_print_chlog_details_replacement(chObject_replacement, clean_tmp):
    log = logging.getLogger('test_print_chlog_details_replacement')

    log.debug('Testing the \'print_chlog_details\' function to '
              'generate a changelog_details_*_replacement file')

    ofiles = chObject_replacement.print_chlog_details(os.getenv('DATADIR')+'/ctree')

    p = re.compile('.*_replacement$')
    m = p.match(ofiles[0])
    m_seen = False
    if m:
        m_seen = True

    # check that the single path in the list exists
    assert os.path.exists(ofiles[0]) == 1
    assert m_seen is True

def test_print_changelog_new(chObject_new, changelog_file, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a new file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a new file')

    chObject_new.print_changelog(ifile=changelog_file.name)

def test_print_changelog_withdrawn(chObject_withdrawn, changelog_file, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a withdrawn file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a withdrawn file')

    chObject_withdrawn.print_changelog(ifile=changelog_file.name)

def test_print_changelog_moved(chObject_moved, changelog_file, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a moved file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a moved file')

    chObject_moved.print_changelog(ifile=changelog_file.name)

def test_print_changelog_replacement(chObject_replacement, changelog_file, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a replacement file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a replacement file')

    chObject_replacement.print_changelog(ifile=changelog_file.name)

def test_update_CHANGELOG(chObject_new, load_changelog_file,
                          push_changelog_file, db_obj, conn_api,
                          dearchive_file, del_from_db, clean_tmp):

    log = logging.getLogger('test_update_CHANGELOG')
    log.debug('Testing the \'update_CHANGELOG\' function')

    CONFIG.set('ctree','backup',os.getenv('DATADIR')+"/ctree/")
    CONFIG.set('ctree', 'chlog_fpath','/ctree/MOCK_CHANGELOG')

    chObject_new.print_changelog(ifile=load_changelog_file.name)
    chObject_new.update_CHANGELOG(load_changelog_file.name, db=db_obj,
                                  api=conn_api)

    del_from_db.append(load_changelog_file.name)
    dearchive_file.append(push_changelog_file)

def test_push_chlog_details(chObject_new, del_from_db, dearchive_file,
                            db_obj, conn_api, clean_tmp):

    log = logging.getLogger('test_push_chlog_details')
    log.debug('Testing the \'push_chlog_details\' function')

    ofiles = chObject_new.print_chlog_details(os.getenv('DATADIR')+"/ctree")

    chObject_new.push_chlog_details(pathlist=ofiles,db=db_obj,
                                    api=conn_api, dry=False)

    for path in ofiles:
        basename = os.path.basename(path)
        new_path = f"{CONFIG.get('ftp', 'ftp_mount')}{CONFIG.get('ctree', 'chlog_details_dir')}/{basename}"
        del_from_db.append(new_path)
        fire_path = f"{CONFIG.get('ctree','chlog_details_dir')}/{os.path.basename(path)}"
        dearchive_file.append(fire_path)

