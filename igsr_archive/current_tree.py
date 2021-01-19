import logging
import pdb

# create logger
ct_logger = logging.getLogger(__name__)

class CurrentTree(object):
    """
    Container for all operations aimed to generate the current.tree and
    related files

    Class variables
    ---------------
    db: DB object
        with connection params
    prod_tree: str
               Path to the 'production tree' file. This is the tree that will
               be the reference in the comparison, i.e. Tree that could
               be allocated in the FTP area. Required
    staging_tree: str
                  Path to the 'staging tree' file. This is the tree that will
                  be the query in the comparison, i.e. New tree generated from
                  the Reseqtrack DB that is located in the 'staging area'

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

    def getKeysByValue(dictOfElements, valueToFind):
        """
        Get a list of keys from dictionary which has the given value
        """
        listOfKeys = list()
        listOfItems = dictOfElements.items()
        for item in listOfItems:
            if item[1] == valueToFind:
                listOfKeys.append(item[0])
        return listOfKeys

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
        5 data_structures in the following order:
        new : set containing the paths that are new in staging vs prod ctree files
        withdrawn : set containing the paths that are removed in staging vs prod ctree files
        moved : containing the file paths (and not the file content) that have
                been modified. This category will contain a dict with the
                following format:
                { 'new_path' : 'old_path'}
        replaced : containing the paths for which the file contents have changed, even
                   if the path stays the same. This category will contain a dict with the
                   following format:
                  { 'path' : tuple ('new_md5', 'old_md5')}
        same : set containing the items that are the same
        """
        d1_keys = set(db_dict.keys())
        d2_keys = set(file_dict.keys())
        shared_keys = d1_keys.intersection(d2_keys)
        new_in_db = d1_keys - d2_keys

        new = d1_keys - d2_keys
        withdrawn = d2_keys - d1_keys
        moved ={} # initialise dict
        for r in new_in_db:
            md5 = db_dict[r]
            # check if file_dict or db_dict contains this 'md5'. Which basically
            # means that file is the same but dir has changed
            pathfdict = [key for (key, value) in file_dict.items() if value == md5]
            pathdbdict = [key for (key, value) in db_dict.items() if value == md5]
            for i, j in zip(pathfdict, pathdbdict):
                print(i, j)
                new.remove(j)
                withdrawn.remove(i)
                moved[j] = i

        # { 'path' : tuple ('new_md5', 'old_md5')}
        replaced = {o: (db_dict[o], file_dict[o]) for o in shared_keys if db_dict[o] != file_dict[o]}
        same = set(o for o in shared_keys if db_dict[o] == file_dict[o])

        return new, withdrawn, moved, replaced, same

    def print_chlog_details(self, new, withdrawn, moved, replaced, same):
        """
        Function to generate 5 changelog details files:
        """


    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()
