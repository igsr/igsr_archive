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
        db_dict = self.db.get_ctree(fields, outfile=self.staging_tree)
        file_dict = self.get_file_dict()

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
        fields = None
        header = False

        data_dict = {}  # dict {'path' : 'md5' }
        with open(self.prod_tree) as f:
            for line in f:
                line = line.rstrip("\n")
                if header is False:
                    fields = line.split("\t")
                    try:
                        ix_md5 = fields.index("md5")
                        ix_name = fields.index("name")
                    except:
                        raise ValueError(f"Either 'md5' or 'name' not found"
                                         f" in the header of f{self.prod_tree}")
                    header = True
                else:
                    name = line.split("\t")[ix_name]
                    md5 = line.split("\t")[ix_md5]
                    data_dict[name] = md5

        return data_dict

    def cmp_dicts(self, db_dict, file_dict):
        """
        Function to compare the 'db_dict' and 'file_dict' dicts and look
        for differences

        Parameters
        ----------
        db_dict : dict
                  Dict in the format { 'name' : 'md5sum' } generated
                  by self.db.get_ctree
        file_dict : dict
                    Dict in the format { 'name' : 'md5sum' } generated
                    by self.get_file_dict
        Returns
        -------
        4 dicts in the following order:
        added : containing the items that are
        removed :
        modified :
        same : containing the items that are the same
        """
        d1_keys = set(db_dict.keys())
        d2_keys = set(file_dict.keys())
        shared_keys = d1_keys.intersection(d2_keys)
        added = d1_keys - d2_keys
        removed = d2_keys - d1_keys
        modified = {o: (db_dict[o], file_dict[o]) for o in shared_keys if db_dict[o] != file_dict[o]}
        same = set(o for o in shared_keys if db_dict[o] == file_dict[o])

        return added, removed, modified, same

