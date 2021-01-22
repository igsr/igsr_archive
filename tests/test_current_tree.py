import pytest
import logging
import os
import glob
import pdb
import re

logging.basicConfig(level=logging.DEBUG)

def test_get_file_dict(ct_obj):
    log = logging.getLogger('test_get_file_dict')

    log.debug('Testing \'get_file_dict\' function')

    data_dict = ct_obj.get_file_dict()

    assert len(data_dict.keys()) == 10

def test_cmp_dicts_new(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_new')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains an additional record')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.minus1.tree"
    file_dict = ct_obj.get_file_dict()
    changeObj = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    assert 'ftp/historical_data/former_toplevel/README.ftp_structure' == list(changeObj.new)[0]

def test_cmp_dicts_withdrawn(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_withdrawn')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains 1 record less than in production current.tree')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.plus1.tree"

    file_dict = ct_obj.get_file_dict()

    changeObj = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    assert 'ftp/release/2009_02/release_02.index' == list(changeObj.withdrawn)[0]

def test_cmp_dicts_replacement(ct_obj, db_dict):
    log = logging.getLogger('test_cmp_dicts_replacement')

    log.debug('Testing \'cmp_dicts\' function in which staging current.tree '
              'contains 2 record that has been replaced with respect to'
              'production current.tree (its md5 has been modified but path '
              'stays the same')

    ct_obj.prod_tree = os.getenv('DATADIR')+"/current.mod.tree"
    file_dict = ct_obj.get_file_dict()
    changeObj = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    actual = sorted(list(changeObj.replacement.keys()))
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
    changeObj = ct_obj.cmp_dicts(db_dict=db_dict, file_dict=file_dict)

    expected = {'ftp/pilot_data/README.alignment.index': 'ftp/pilot_data1/README.alignment.index'}

    assert changeObj.moved == expected
