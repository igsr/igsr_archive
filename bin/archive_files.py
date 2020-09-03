#!/usr/bin/env python

import argparse
import os
import logging
import sys
import re
import pdb
from igsr_archive.utils import str2bool
from igsr_archive.db import DB
from igsr_archive.api import API
from igsr_archive.file import File
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script for interacting with the FIle REplication (FIRE) software. '\
                                             'This script can be used for archiving files in the public '\
                                             'IGSR FTP. Once a certain file is archived using this script, it will be '\
                                             'accessible from our IGSR public FTP.')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")

parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to archive the file without "
                                                "effectively doing it. True: Perform a dry-run")
parser.add_argument('-f', '--file', help="Path to file to be archived in FIRE. This script assumes that file"
                                         "is placed in the staging area of our filesystem ")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing a list of files "
                                                                           "to archive (one per line). Each of "
                                                                           "the files need to be placed in the"
                                                                           " staging area of our filesystem")
parser.add_argument('--type',  help="New file type used in the Reseqtrack DB for archiving the files")
parser.add_argument('--update_existing', default=False, help="If True, then update a file that is already archived "
                                                             "in the FTP with the new file that is placed in the "
                                                             "staging area")
parser.add_argument('--dbpwd', help="Password for MYSQL server. If not provided then it will try to guess"
                                    "the password from the $DBPWD env variable")
parser.add_argument('--dbname', help="Database name. If not provided then it will try to guess"
                                     "the dbname from the $DBNAME env variable")
parser.add_argument('--firepwd', help="FIRE api password. If not provided then it will try to guess"
                                      "the FIRE pwd from the $FIRE_PWD env variable")
parser.add_argument('--log', default='INFO', help="Logging level. i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL")

args = parser.parse_args()

# logging
loglevel = args.log
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(level=numeric_level)

# Create logger
logger = logging.getLogger(__name__)

logger.info('Running script')

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

dbpwd = args.dbpwd
if args.dbpwd is None:
    dbpwd = os.getenv('DBPWD')

dbname = args.dbname
if args.dbname is None:
    dbname = os.getenv('DBNAME')

firepwd = args.firepwd
if args.firepwd is None:
    firepwd = os.getenv('FIRE_PWD')

if dbname is None:
    raise Exception("$DBNAME undefined. You need either to pass the name of the "
                    "RESEQTRACK database using the --dbname option or set a $DBNAME "
                    "environment variable before running this script!")
if dbpwd is None:
    raise Exception("$DBPWD undefined. You need either to pass the password of the MYSQL "
                    "server containing the RESEQTRACK database using the --dbpwd option or set a $DBPWD environment "
                    "variable before running this script!")
if firepwd is None:
    raise Exception("$FIRE_PWD undefined. You need either to pass the FIRE API password using the --firepwd option"
                    " or set a $FIRE_PWD environment variable before running this script!")

# list of tuples (origin, dest) for files to be archived
files = []
if args.file:
    logger.info('File provided using -f, --file option')
    abs_path = os.path.abspath(args.file)
    files.append(abs_path)
elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')

    for line in args.list_file:
        line = line.rstrip("\n")
        abs_path = os.path.abspath(line)
        files.append(abs_path)

# check if user has passed any file
if len(files) == 0:
    logger.info('No file/s provided. Nothing to be done...')
    sys.exit(0)

# connection to Reseqtrack DB
db = DB(settingsf=args.settings,
        pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(settingsf=args.settings,
          pwd=firepwd)

for f in files:
    fireObj = None

    # check if path exists
    if not os.path.isfile(f):
        raise Exception(f"File path to be archived: {f} does not exist. Can't continue!")
    # check if staging mount point exists in file path to be archived
    if not settingsO.get('ftp', 'staging_mount') in f:
        raise Exception(f"File to be archived: {f} is not placed in the staging area:"
                        f" {settingsO.get('ftp', 'staging_mount')}.\nYou need to move it first. Can't continue!")
    fire_path = re.sub(settingsO.get('ftp', 'staging_mount')+"/", '', f)
    ftp_path = os.path.join(settingsO.get('ftp', 'ftp_mount'), fire_path)

    # check if 'f' exists in db and fetch the file
    f_indb_o = db.fetch_file(path=f)

    # check if this file is already in the ftp
    f_inftp_o = db.fetch_file(path=ftp_path)

    if f_indb_o is None and f_inftp_o is not None:
        if str2bool(args.update_existing) is True:
            # 'f' that is in the staging area does not exist in DB, but it does exist in the FTP
            # This means that user wants to update a file that is already in te FTP.
            logger.info(f"It seems that file: {f} is already archived and --update_existing is True")
            logger.info(f"Archived file will be updated with new file")

            # First, retrieve the FIRE object
            dearch_fobj = api.fetch_object(firePath=fire_path)

            assert dearch_fobj is not None, f"Object with FIRE path: {fire_path} was not retrieved"

            # delete the FIRE object
            api.delete_object(fireOid=dearch_fobj.fireOid,
                              dry=str2bool(args.dry))

            # Create File object pointing to the file placed in the staging area
            f_in_staging = File(name=f)

            # now update the metadata for f_inftp_o
            status_code = db.update_file(attr_name='md5',
                                         value=f_in_staging.md5,
                                         name=ftp_path,
                                         dry=str2bool(args.dry))
            assert status_code == 0, "Something went wrong when updating the 'md5' field of the entry in the 'File'" \
                                     "table of the the DB"

            status_code = db.update_file(attr_name='size',
                                         value=f_in_staging.size,
                                         name=ftp_path,
                                         dry=str2bool(args.dry))
            assert status_code == 0, "Something went wrong when updating the 'size' field of the entry in the 'File'" \
                                     "table of the the DB"

            # Now, push the new file
            # push the file to FIRE where fire_path will the path in the FIRE
            # filesystem
            fireObj = api.push_object(fileO=f_in_staging,
                                      dry=str2bool(args.dry),
                                      fire_path=fire_path)
        elif str2bool(args.update_existing) is False:
            logger.info(f"It seems that file: {f} is already archived and --update_existing is False")
            logger.info(f"Archived file will not be updated with new file")
    elif f_indb_o is not None and f_inftp_o is None:
        # 'f' does not exist in the FTP, archive it as a new file
    
        # push the file to FIRE where fire_path will the path in the FIRE
        # filesystem
        fireObj = api.push_object(fileO=f_indb_o,
                                  dry=str2bool(args.dry),
                                  fire_path=fire_path)

        # now, modify the file entry in the db and update its name (path)
        ret_db_code = db.update_file(attr_name='name',
                                     value=ftp_path,
                                     name=f,
                                     dry=str2bool(args.dry))
    elif f_indb_o is None and f_inftp_o is None:
        # 'f' does not exist neither the DB nor the FTP. Raise exception
        raise Exception(f"File entry with path {f} does not exist in the DB. "
                        f"You need to load it first in order to proceed")

    if args.type:
        logger.info(f"--type option provided. Its value will be used for updating"
                    f" the file type in {args.dbname}")

        status_code = db.update_file(attr_name='type',
                                     value=args.type,
                                     name=ftp_path,
                                     dry=str2bool(args.dry))
        assert status_code == 0, "Something went wrong when updating the 'type' field of the entry in the 'File'" \
                                 "table of the the DB"

    # Finally, delete the file that has been pushed
    if str2bool(args.dry) is False:
        if fireObj is not None:
            logger.info(f"File successfully pushed and correctly updated in the DB")
            logger.info(f"File {f} will be removed")
            os.remove(f)

