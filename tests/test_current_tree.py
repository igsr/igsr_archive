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
                         prod_tree=os.getenv('DATADIR')+"/current.tree")

    return ct_obj

def test_get_file_dict(ct_obj):
    log = logging.getLogger('test_get_file_dict')

    log.debug('Testing \'get_file_dict\' function')

    data_dict = ct_obj.get_file_dict()

    assert len(data_dict.keys()) == 10
    assert 0
