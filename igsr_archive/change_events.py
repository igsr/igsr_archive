import logging
import pdb
import os

from igsr_archive.file import File
from datetime import datetime
from igsr_archive.config import CONFIG

# create logger
ce_logger = logging.getLogger(__name__)

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

        ce_logger.debug('Creating ChangeEvents object')

        self.new = new
        self.withdrawn = withdrawn
        self.moved = moved
        self.replacement = replacement
        self.dtime = datetime.now()

    def size(self):
        """
        Calculate the length of this object
        Length is defined as the number of paths
        having changes

        Returns
        -------
        int: Number of changes
        """
        size = 0
        for state, value in self.__dict__.items():
            if type(value) is set:
                size = size + len(value)
            elif type(value) is dict:
                size = size + len(value.keys())
        return size

    def print_chlog_details(self, odir):
        """
        Function to generate the changelog_details files
        These filenames contain the information on the changes between staging and prod
        ctree files

        Parameters
        ----------
        odir : directory name for placing the changelog_details files

        Returns
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
        ifile : path to CHANGELOG file that will be updated
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

    def update_CHANGELOG(self, chlog, db, api):
        """
        Function to push the updated CHANGELOG file
        to FIRE. This function will do the following:

        1) Update the CHANGELOG file metadata in the DB
        2) Create a backup copy of the CHANGELOG file before being updated
        3) Delete the old CHANGELOG file from FIRE
        4) Push the new (updated) CHANGELOG file to FIRE
        5) Delete the backed-up file if everything went well

        Parameters
        ----------
        chlog : File object
                updated CHANGELOG file that will be pushed to FIRE
        db : DB connection object
        api : API connection object

        Returns
        -------
        path : Fire path of the updated CHANGELOG files
        """
        # update the CHANGELOG metadata in the DB
        chlog.md5 = chlog.calc_md5()
        chlog.size = os.path.getsize(chlog.name)
        db.update_file('md5', chlog.md5, chlog.name, dry=False)
        db.update_file('size', chlog.size, chlog.name, dry=False)

        ce_logger.info("Pushing updated CHANGELOG file to API")
        # to push the updated CHANGELOG you need to delete it from FIRE first
        old_file = api.retrieve_object(firePath=CONFIG.get('ctree','chlog_fpath'),
                                       outfile=f"{CONFIG.get('ctree','backup')}/{os.path.basename(chlog.name)}.backup")
        if old_file is None:
            raise Exception(f"No CHANGELOG file retrieved from the archive")

        fire_obj = api.fetch_object(firePath=CONFIG.get('ctree','chlog_fpath'))

        if fire_obj is None:
            raise Exception(f"No CHANGELOG file retrieved from the archive")

        ce_logger.info("Delete CHANGELOG to be updated from the archive")
        api.delete_object(fireOid=fire_obj.fireOid, dry=False)

        ce_logger.info("Push updated CHANGELOG file to the archive")
        api.push_object(chlog, dry=False, fire_path=CONFIG.get('ctree','chlog_fpath'))

        return f"{CONFIG.get('ctree','chlog_fpath')}"

    def push_chlog_details(self, pathlist, db, api):
        """
        Function to push the change changelog_details_* files to the archive.
        This function will do the following:

        1) Load the new changelog_details_* files to the DB
        2) Push the new changelog_details_* files to the archive

        Parameters
        ----------
        pathlist : list
                   List with the paths of the changelog_details_* files
                   (resulting from running self.print_chlog_details)
        db : DB connection object
        api : API connection object

        Returns
        -------
        list : list with the Fire paths of the pushed changelog_details_*
        """
        ce_logger.info("Pushing changelog_details_* files to the archive")

        pushed_files = []
        for p in pathlist:
            basename= os.path.basename(p)
            fObj = File(name=p, type="CHANGELOG")
            new_path = f"{CONFIG.get('ftp','ftp_mount')}{CONFIG.get('ctree','chlog_details_dir')}/{basename}"
            db.load_file(fObj, dry=False)
            api.push_object(fObj, dry=False, publish=True,
                            fire_path=f"{CONFIG.get('ctree', 'chlog_details_dir')}/{basename}")
            pushed_files.append(f"{CONFIG.get('ctree', 'chlog_details_dir')}/{basename}")
            db.update_file('name', new_path, fObj.name, dry=False)

        return pushed_files



    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()