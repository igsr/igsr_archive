import logging
import pdb
import os

from igsr_archive.change_events import ChangeEvents

# create logger
ct_logger = logging.getLogger(__name__)

class CurrentTree(object):
    """
    Container for all operations aimed to generate the current.tree and
    related files

    Class variables
    ---------------
    db: DB object. Required
    api: FIRE api object. Required
    prod_tree: str
               Path to the 'production tree' file. This is the tree that will
               be the reference in the comparison, i.e. Tree that could
               be allocated in the FTP area. Required
    staging_tree: str
                  Path to the 'staging tree' file. This is the tree that will
                  be the query in the comparison, i.e. New tree generated from
                  the Reseqtrack DB that is located in the 'staging area'. Required

    """
    def __init__(self, db, api, prod_tree, staging_tree):

        ct_logger.debug('Creating CurrentTree object')

        self.db = db
        self.api = api
        self.prod_tree = prod_tree
        self.staging_tree = staging_tree

    def run(self, chlog_fpath, chlog_name='CHANGELOG'):
        """
        Function to perform all operations involved in the comparison
        between the current.tree in the DB and the current.tree in the FTP

        Parameters
        ----------
        chlog_fpath: string
                     Fire path for CHANGELOG file (i.e. ). Required
        chlog_name: string
                    Basename for the file used to add the new CHANGELOG entry
                    Default: CHANGELOG

        Returns
        -------
        0 if run was successful, 1 otherwise
        """
        wd = os.path.dirname(self.staging_tree)

        fields = ['name', 'size', 'updated', 'md5']
        db_dict = self.db.get_ctree(fields, outfile=self.staging_tree, limit=10)[1]
        file_dict = self.get_file_dict()
        chgEvents = self.cmp_dicts(db_dict=db_dict, file_dict=file_dict)
        if chgEvents.size() == 0:
            ct_logger.info("No changes detected, nothing will be done. "
                           "The current.tree file in the staging area will be removed")
            os.remove(self.staging_tree)
            return 0
        else:
            pdb.set_trace()
            ct_logger.info("Changes detected in the data structures. Proceeding...")
            ct_logger.info("Generating chlog_details_* files")
            ofiles = chgEvents.print_chlog_details(odir=wd)
            ct_logger.info("Fetching CHANGELOG file from archive")
            chlog_obj = self.db.fetch_file(basename=chlog_name)
            ct_logger.info("Updating CHANGELOG file in the DB")
            chgEvents.print_changelog(ifile=chlog_obj.name)
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
        ChangeEvents object
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
        replacement = {o: (db_dict[o], file_dict[o]) for o in shared_keys if db_dict[o] != file_dict[o]}

        return ChangeEvents(new, withdrawn, moved, replacement)

    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()