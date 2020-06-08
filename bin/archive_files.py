#!/usr/bin/env python

import argparse
import os
import logging
import sys
import re
from igsr_archive.utils import str2bool
from igsr_archive.db import DB
from igsr_archive.api import API
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script for interacting with the FIle REplication (FIRE) software. '\
                                             'This script can be used for archiving files in the public '\
                                             'IGSR FTP. Once a certain file is archived using this script, it will be '\
                                             'accessible from our IGSR public FTP.')

parser.add_argument('-s', '--settingsf', required=True,
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

if not os.path.isfile(args.settingsf):
    raise Exception(f"Config file provided using --settingsf option({args.settingsf}) not found!")

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settingsf)

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
db = DB(settingf=args.settingsf,
        pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(settingsf=args.settingsf,
          pwd=firepwd)

for f in files:
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
    f_obj = db.fetch_file(path=f)
    assert f_obj is not None, f"File entry with path {f} does not exist in the DB. "\
                              f"You need to load it first in order to proceed"
    # now, check if 'dest' exists in db
    assert db.fetch_file(path=ftp_path) is None, f"File entry with path {ftp_path} already exists in the FTP archive."\
                                                 f"It will not continue trying to archive this file"

    # push the file to FIRE where fire_path will the path in the FIRE
    # filesystem
    api.push_object(fileO=f_obj,
                    dry=str2bool(args.dry),
                    fire_path=fire_path)

    # now, modify the file entry in the db and update its name (path)
    db.update_file(attr_name='name',
                   value=ftp_path,
                   name=f,
                   dry=str2bool(args.dry))

    if args.type:
        logger.info(f"--type option provided. Its value will be used for updating"
                    f" the file type in {args.dbname}")

        db.update_file(attr_name='type',
                       value=args.type,
                       name=ftp_path,
                       dry=str2bool(args.dry))
