import logging
import pdb

from igsr_archive.file import File

from datetime import datetime

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

class ChangeEvents(object):
    """
    Container encapsulating a change/s in the state of self.staging_tree vs
    self.prod_tree

    Class variables
    ---------------
    new : set containing the paths that are new in staging vs prod ctree files
    withdrawn : set containing the paths that are removed in staging vs prod ctree files
    moved : containing the file paths (and not the file content) that have
            been modified. This category will contain a dict with the
            following format:
            { 'new_path' : 'old_path'}
    replacement : containing the paths for which the file contents have changed, even
                  if the path stays the same. This category will contain a dict with the
                  following format:
                  { 'path' : tuple ('new_md5', 'old_md5')}
    datetime : datetime object
               When this object has been created
    """
    def __init__(self, new, withdrawn, moved, replacement):

        ct_logger.debug('Creating ChangeEvents object')

        self.new = new
        self.withdrawn = withdrawn
        self.moved = moved
        self.replacement = replacement
        self.dtime = datetime.now()

    def print_chlog_details(self, odir):
        """
        Function to generate the changelog_details files
        These filenames contain the information on the changes between staging and prod
        ctree files

        Parameters
        ----------
        odir : directory name for placing the changelog_details files

        returns
        -------
        list : list with the file paths of the new
               changelog_details_* files
        """
        now_str = self.dtime.strftime('%Y%m%d')

        ofiles_lst = []
        if len(self.new) > 0:
            ofile_new = open("{0}/changelog_details_{1}_new".format(odir, now_str), 'w')
            for i in self.new:
                ofile_new.write(i + "\n")
            ofile_new.close()
            ofiles_lst.append(ofile_new.name)
        elif len(self.withdrawn) > 0:
            ofile_with = open("{0}/changelog_details_{1}_withdrawn".format(odir, now_str), 'w')
            for i in self.withdrawn:
                ofile_with.write(i + "\n")
            ofile_with.close()
            ofiles_lst.append(ofile_with.name)
        elif len(self.moved) > 0:
            ofile_moved = open("{0}/changelog_details_{1}_moved".format(odir, now_str), 'w')
            for f in self.moved.keys():
                ofile_moved.write("{0}\t{1}\n".format(self.moved[f], f))
            ofile_moved.close()
            ofiles_lst.append(ofile_moved.name)
        elif len(self.replacement) > 0:
            ofile_replc = open("{0}/changelog_details_{1}_replacement".format(odir, now_str), 'w')
            for f in self.replacement.keys():
                ofile_replc.write(f + "\n")
            ofile_replc.close()
            ofiles_lst.append(ofile_replc.name)

        return ofiles_lst

    def print_changelog(self, ifile):
        """
        Function that adds an entry to the CHANGELOG report
        file

        Parameters
        ----------
        ifile : path to CHANGELOG file
        """
        now_str = self.dtime.strftime('%Y-%m-%d')
        now_str1 = self.dtime.strftime('%Y%m%d')
        try:
            f = open(ifile, 'a')
            f.write(now_str+"\n\n")
            for state, value in self.__dict__.items():
                size = 0
                if type(value) is set:
                    size = len(value)
                elif type(value) is dict:
                    size = len(value.keys())
                if size == 0: continue
                types = []
                for p in value:
                    # create File object to get its type
                    fObj = File(name=p)
                    types.append(fObj.guess_type())
                f.write("Modification to: {0}\n\n".format(",".join(types)))
                f.write("Details can be found in\nchangelog_details/changelog_details_{0}_{1}\n\n".format(now_str1, state))
        except FileNotFoundError:
            print('File does not exist')
        finally:
            f.close()

    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()