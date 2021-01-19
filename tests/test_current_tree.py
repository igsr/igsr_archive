import pytest
import logging
import os
import pdb

from igsr_archive.current_tree import CurrentTree

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def ct_obj(db_obj):
    '''
    Returns a CurrentTree object
    '''
    log = logging.getLogger('ctree_obj')
    log.debug('Create a CurrentTree object')

    ct_obj = CurrentTree(db=db_obj,
                         staging_tree=os.getenv('DATADIR')+"/current.new.tree",
                         prod_tree=os.getenv('DATADIR')+"/current.same.tree")
    return ct_obj

@pytest.fixture
def db_dict(db_obj):
    '''
    Returns a dict from the records in DB
    '''
    log = logging.getLogger('db_dict')

    log.debug('Fixture for getting a data dict from DB')

    fields = ['name', 'size', 'updated', 'md5']
    # limit the number of records to 10
    ctree_path, data_dict = db_obj.get_ctree(fields, outfile=os.getenv('DATADIR') + "/current.new.tree", limit=10)

    return data_dict

def test_get_file_dict(ct_obj):
    log = logging.getLogger('test_get_file_dict')

    log.debug('Testing \'get_file_dict\' function')

    data_dict = ct_obj.get_file_dict()

    assert len(data_dict.keys()) == 10

def test_cmp_dicts_same(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_same')

    log.debug('Testing \'cmp_dicts\' function in which prod/staging current.tree '
              'are the same')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.same.tree"

    file_dict = ct_obj.get_file_dict()

    new, withdrawn, moved, replaced, same = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    assert len(new) == 0
    assert len(withdrawn) == 0
    assert len(moved) == 0
    assert len(replaced) == 0
    assert len(same) == 10

def test_cmp_dicts_new(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_new')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains an additional record')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.minus1.tree"

    file_dict = ct_obj.get_file_dict()

    new, withdrawn, moved, replaced, same = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    assert len(new) == 1
    assert len(withdrawn) == 0
    assert len(moved) == 0
    assert len(replaced) == 0
    assert len(same) == 9

def test_cmp_dicts_withdrawn(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_withdrawn')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains 1 record less than in production current.tree')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.plus1.tree"

    file_dict = ct_obj.get_file_dict()

    new, withdrawn, moved, replaced, same = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    assert len(new) == 0
    assert len(withdrawn) == 1
    assert len(moved) == 0
    assert len(replaced) == 0
    assert len(same) == 10

def test_cmp_dicts_replaced(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_replaced')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains 2 record that has been replaced with respect to'
              'production current.tree (its md5 has been modified but path '
              'stays the same')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.mod.tree"

    file_dict = ct_obj.get_file_dict()
    new, withdrawn, moved, replaced, same = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    assert len(new) == 0
    assert len(withdrawn) == 0
    assert len(moved) == 0
    actual = sorted(list(replaced.keys()))
    expected = ['/nfs/1000g-work/G1K/archive_staging/ftp/current.tree',
                'ftp/pilot_data/README.alignment.index']

    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])

def test_cmp_dicts_moved(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_moved')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains 1 record that has been moved with respect to'
              'production current.tree (its md5 stays the same but path'
              'has changed')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.moved.tree"

    file_dict = ct_obj.get_file_dict()
    new, withdrawn, moved, replaced, same = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    expected = {'ftp/pilot_data/README.alignment.index': 'ftp/pilot_data1/README.alignment.index'}

    assert len(new) == 0
    assert len(withdrawn) == 0
    assert moved == expected
    assert len(replaced) == 0
    assert len(same) == 9
