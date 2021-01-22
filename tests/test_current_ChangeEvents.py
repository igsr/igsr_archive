import pytest
import logging
import os
import glob
import pdb
import re

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def clean_tmp():
    yield
    log = logging.getLogger('clean_tmp')
    log.debug('Cleaning tmp files')

    files = glob.glob(os.getenv('DATADIR')+'/changelog_details_*')
    for f in files:
        os.remove(f)

    # delete CHANGELOG file
    files1 = glob.glob(os.getenv('DATADIR')+'/CHANGELOG')
    for f in files1:
        os.remove(f)

@pytest.fixture
def chObject_new(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a new path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "/current.minus1.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture
def chObject_withdrawn(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a withdrawn path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "/current.plus1.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture
def chObject_moved(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a moved path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "/current.moved.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

@pytest.fixture
def chObject_replacement(ct_obj, db_dict):
    """
    Fixture returning a ChangeEvents object
    with a replacement path
    """
    ct_obj.prod_tree = os.getenv('DATADIR') + "/current.mod.tree"
    file_dict = ct_obj.get_file_dict()
    chObject = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    return chObject

def test_print_chlog_details_new(chObject_new, clean_tmp):
    log = logging.getLogger('test_print_chlog_details_new')

    log.debug('Testing the \'print_chlog_details\' function to '
              'generate a changelog_details_*_new file')

    ofiles = chObject_new.print_chlog_details(os.getenv('DATADIR'))

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

    ofiles = chObject_withdrawn.print_chlog_details(os.getenv('DATADIR'))

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

    ofiles = chObject_moved.print_chlog_details(os.getenv('DATADIR'))

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

    ofiles = chObject_replacement.print_chlog_details(os.getenv('DATADIR'))

    p = re.compile('.*_replacement$')
    m = p.match(ofiles[0])
    m_seen = False
    if m:
        m_seen = True

    # check that the single path in the list exists
    assert os.path.exists(ofiles[0]) == 1
    assert m_seen is True

def test_print_changelog_new(chObject_new, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a new file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a new file')

    chglog_f = os.getenv('DATADIR') + "/CHANGELOG"
    chObject_new.print_changelog(ifile=chglog_f)

def test_print_changelog_withdrawn(chObject_withdrawn, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a withdrawn file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a withdrawn file')

    chglog_f = os.getenv('DATADIR') + "/CHANGELOG"
    chObject_withdrawn.print_changelog(ifile=chglog_f)

def test_print_changelog_moved(chObject_moved, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a moved file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a moved file')

    chglog_f = os.getenv('DATADIR') + "/CHANGELOG"
    chObject_moved.print_changelog(ifile=chglog_f)

def test_print_changelog_replacement(chObject_replacement, clean_tmp):
    """
    Test function 'print_changelog'

    This test will create a mock CHANGELOG
    file and will add an entry to it representing
    a replacement file
    """
    log = logging.getLogger('test_print_changelog')
    log.debug('Testing the \'print_changelog\' function'
              ' with a replacement file')

    chglog_f = os.getenv('DATADIR') + "/CHANGELOG"
    chObject_replacement.print_changelog(ifile=chglog_f)