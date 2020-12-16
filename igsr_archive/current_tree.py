import logging
import pdb

# create logger
ct_logger = logging.getLogger(__name__)

class CurrentTree(object):
    """
    Container for all operations aimed to generate the current.tree and
    related files
    """
    def __init__(self, db, prod_tree, staging_tree):

        ct_logger.debug('Creating CurrentTree object')

        self.db = db
        self.prod_tree = prod_tree
        self.staging_tree = staging_tree

    def run(self):
        """
        Function to perform all operations
        """

        fields = ['name', 'size', 'updated']
        self.db.get_ctree(fields, outfile=self.stating_tree, limit=10)
        pdb.set_trace()
        print("h")

    def get_file_dict(self):
        """
        Function to parse each line in the file pointed by self.prod_tree
        to create a dict with the following information:
        { 'path' : md5 }

        Returns
        -------
        dict
        """

    def cmp_dicts(self):
        """
        Function to compare the 'dict1' and 'dict2' dicts and look
        for differences
        """
