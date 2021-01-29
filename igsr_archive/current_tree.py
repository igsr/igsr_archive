import logging
import pdb
import os
import datetime

from igsr_archive.change_events import ChangeEvents
from igsr_archive.file import File
from igsr_archive.config import CONFIG
from datetime import datetime

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
    dtime: str
              Str with the datetime this object was instantiated
    """
    def __init__(self, db, api, prod_tree, staging_tree):

        ct_logger.debug('Creating CurrentTree object')

        self.db = db
        self.api = api
        self.prod_tree = prod_tree
        self.staging_tree = staging_tree
        self.dtime = datetime.now().strftime('%Y_%m_%dT%H%M%S')

    def run(self, chlog_fobj):
        """
        Function to perform all operations involved in the comparison
        between the current.tree in the DB and the current.tree in the FTP

        Parameters
        ----------
        chlog_fobj: File
                    File object for CHANGELOG file. Required
        Returns
        -------
        If there is a ChangeEvents with entries in it then it will generate a dict
        with the following format:

         {'chlog_details' : chlog_details_list,
         'chlog_firepath' : chlog_firepath,
         'ctree_firepath' : ctree_firepath}

        If the ChangeEvents object has size = 0 then it will return 0
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
            ct_logger.info("Changes detected in the data structures. Proceeding...")
            ofiles = chgEvents.print_chlog_details(odir=wd)
            chlog_details_list = chgEvents.push_chlog_details(pathlist=ofiles, db=self.db, api=self.api)
            chgEvents.print_changelog(ifile=chlog_fobj.name)
            chlog_firepath = chgEvents.update_CHANGELOG(chlog_fobj, db=self.db, api=self.api)
            ctree_firepath= self.push_ctree()
            return {
                'chlog_details' : chlog_details_list,
                'chlog_firepath' : chlog_firepath,
                'ctree_firepath' : ctree_firepath
            }

    def push_ctree(self):
        """
        Function to push self.staging_tree to the archive.
        This function will follow these steps:
        1) Update the metadata for current.tree entry in the DB
        2) Create a backup for self.prod_tree
        3) Delete self.prod_tree
        4) Push self.staging_tree to the archive

        Returns
        -------
        path : Fire path of the pushed current.tree

        """
        # updating metadata for existing staging_tree file in the DB
        staging_fobj = File(name=self.staging_tree)
        self.db.update_file('md5',staging_fobj.md5, staging_fobj.name, dry=False)
        self.db.update_file('size',staging_fobj.size, staging_fobj.name, dry=False)

        # create a backup for self.prod_tree
        basename = os.path.basename(self.prod_tree)
        fire_path = f"{CONFIG.get('ctree', 'ctree_fpath')}/{basename}"
        prod_file = self.api.retrieve_object(firePath=fire_path,
                                            outfile=f"{CONFIG.get('ctree', 'backup')}/{basename}."
                                                    f"{self.dtime}.backup")

        if prod_file is None:
            raise Exception(f"No current.tree file retrieved from the archive")

        # delete self.prod_tree from archive
        fire_obj = self.api.fetch_object(firePath=fire_path)

        if fire_obj is None:
            raise Exception(f"No current.tree file retrieved from the archive")
        self.api.delete_object(fireOid=fire_obj.fireOid, dry=False)

        # push self.staging_tree to archive
        basename = os.path.basename(self.staging_tree)
        fire_path = f"{CONFIG.get('ctree', 'ctree_fpath')}/{basename}"
        self.api.push_object(fileO=staging_fobj,
                             fire_path=fire_path,
                             dry=False)
        return fire_path

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