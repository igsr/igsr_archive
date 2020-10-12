#!/usr/bin/env python

import argparse
import os
import logging
import sys
import re
import pdb
import glob
from igsr_archive.utils import str2bool
from igsr_archive.db import DB
from igsr_archive.api import API
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script for interacting with the FIle REplication (FIRE) software. '\
                                             'This script can be used for moving files within the FTP.'
                                             'It will also update the file metadata for the moved file in the '
                                             'RESEQTRACK database')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")

parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to archive the file without "
                                                "effectively doing it. True: Perform a dry-run")
parser.add_argument('--origin', help="Path to the archived file in the FTP to be moved")
parser.add_argument('--dest', help="Final path of file in the FTP")
parser.add_argument('--src_dir', help="Source directory containing files in the FTP")
parser.add_argument('--tg_dir', help="Target directory where the files in --src_dir will be moved")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="2-columns file containing the paths to"
                                                                           " the archived files in the FTP that are going"
                                                                           " to be moved and the final paths of the "
                                                                           "files in the FTP, one in each line")
parser.add_argument('--dbpwd', help="Password for MYSQL server. If not provided then it will try to guess "
                                    "the password from the $DBPWD env variable")
parser.add_argument('--dbname', help="Database name. If not provided then it will try to guess the dbname"
                                     " from the $DBNAME env variable")
parser.add_argument('--firepwd', help="FIRE api password. If not provided then it will try to guess the FIRE"
                                      " pwd from the $FIRE_PWD env variable")
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

dbpwd = args.dbpwd
if args.dbpwd is None:
    dbpwd = os.getenv('DBPWD')

dbname = args.dbname
if args.dbname is None:
    dbname = os.getenv('DBNAME')

firepwd = args.firepwd
if args.firepwd is None:
    firepwd = os.getenv('FIRE_PWD')

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

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

origin_seen = False
src_dir_seen = False
if args.origin or args.dest:
    origin_seen = True
    assert args.dest and args.dest, "--origin and --dest args need to be defined"
elif args.src_dir or args.tg_dir:
    src_dir_seen = True
    assert args.src_dir and args.tg_dir, "--src_dir and --tg_dir args needs to be defined"
elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')

    for line in args.list_file:
        line = line.rstrip("\n")
        try:
            origin, dest = line.split("\t")
            files.append((origin, dest))
        except Exception:
            raise Exception("Format of file provided with --list_file, -l option needs to be:"
                            "<origin>\\t<dest>")

if origin_seen is True:
    logger.info('--origin and --dest args defined')
    files.append((args.origin, args.dest))
elif src_dir_seen is True:
    logger.info('--src_dir and --tg_dir args defined')
    for origin in glob.glob(f"{args.src_dir}"):
        # get absolute paths
        origin = os.path.abspath(origin)
        basename = os.path.basename(origin)
        dest = f"{os.path.abspath(args.tg_dir)}/{basename}"
        files.append((origin, dest))

# check if user has passed any file
if len(files) == 0:
    logger.info('No file/s provided. Nothing to be done...')
    sys.exit(0)

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

# connection to Reseqtrack DB
db = DB(settingsf=args.settings,
        pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(settingsf=args.settings,
          pwd=firepwd)

for tup in files:
    # check if 'origin' exists in db and fetch the file
    origin_f = db.fetch_file(path=tup[0])
    assert origin_f is not None, f"File entry with path {tup[0]} does not exist in the DB. "\
                                 f"Can't move the file"

    # now, check if 'dest' exists in db
    assert db.fetch_file(path=tup[1]) is None, f"File entry with path {tup[1]} already exists in the DB."\
                                               f"It will not continue"

    assert os.path.basename(tup[0]) == os.path.basename(tup[1]), f"{ os.path.basename(tup[0])} and" \
                                                                 f" {os.path.basename(tup[1])}" \
                                                                 f" does not match. Can't continue!"

    # getting the fire_path to be moved
    f_path_origin = re.sub(settingsO.get('ftp', 'ftp_mount') + "/", '', tup[0])
    f_path_dest = re.sub(settingsO.get('ftp', 'ftp_mount') + "/", '', tup[1])

    # getting the fire object that will be updated
    fobject = api.fetch_object(firePath=f_path_origin)

    # update the FIRE object with the new firePath
    updated_obj = api.update_object(attr_name='firePath',
                                    value=f_path_dest,
                                    fireOid=fobject.fireOid,
                                    dry=str2bool(args.dry))

    # now, modify the file entry in the db and update its name (path)
    db.update_file(attr_name='name',
                   value=tup[1],
                   name=tup[0],
                   dry=str2bool(args.dry))