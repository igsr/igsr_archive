#!/usr/bin/env python
import argparse
import os
import re
import logging
import sys

from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script for dearchiving (i.e. removing) a file or a list of files from '\
                                             'our public FTP. This script will download the file to be dearchived to '\
                                             'a desired location before dearchiving from FIRE and will also delete the '\
                                             'entry in the `file` table from the `RESEQTRACK` database.')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('--dry', default=True,
                    help="Perform a dry-run and attempt to dearchive the file without "
                         "effectively doing it. True: Perform a dry-run")
parser.add_argument('--md5check', default=True,
                    help="Check if md5sum of downloaded file and FIRE object matches before dearchiving from FIRE")
parser.add_argument('-f', '--file', help="Path to file to be dearchived. It must exists in the g1k_archive_staging_track DB")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing the paths of the files to"
                                                                           "be dearchived")                                                                  
parser.add_argument('-d', '--directory', required=True, help="Directory used for storing the dearchived file")
parser.add_argument('-tid', '--ticket', help="The ticket number from the RT ticket created by the collaborator" )
parser.add_argument('--dbpwd', help="Password for MYSQL server. If not provided then it will try to guess"
                                    "the password from the $DBPWD env variable")
parser.add_argument('--dbname', help="Database name. If not provided then it will try to guess"
                                     "the dbname from the $DBNAME env variable")
parser.add_argument('--firepwd', help="FIRE api password. If not provided then it will try to guess"
                                      "the FIRE pwd from the $FIRE_PWD env variable")
parser.add_argument('--log', default='INFO', help="Logging level. i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL")

args = parser.parse_args()

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# set the CONFIG_FILE env variable
os.environ["CONFIG_FILE"] = os.path.abspath(args.settings)

from igsr_archive.utils import str2bool
from igsr_archive.db import DB
from igsr_archive.api import API
from igsr_archive.file import File



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

assert firepwd, "$FIRE_PWD undefined"
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

if not os.path.isdir(args.directory):
    raise Exception(f"{args.directory} does not exist. Can't continue!")

if args.ticket is None:
    raise Exception("$ticket_id undefined. You need this to keep track of the tickets. Please add this by using the option -tid or --ticket")

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

# connection to Reseqtrack DB
db = DB(pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(pwd=firepwd)

# list of tuples (origin, dest) for files to be archived
files = []

if args.file:
    logger.info("File provided")
    files.append(args.file)
elif args.list_file:
    logger.info("List of files to dearchive provided")
    for line in args.list_file:
        line = line.rstrip("\n")
        files.append(line)

for path in files:
    # there is no need for it to take the abspath 
    #abs_path = os.path.abspath(path)
    #fire_path = re.sub(settingsO.get('ftp', 'ftp_mount') + "/", '', os.path.abspath(path))

    if re.search("/", path) :
        #adding a die if the path does not start with nfs
        if path.startswith("/nfs") is False :
            sys.exit()
        dearch_f = db.fetch_file(path=path)
    else:
        dearch_f = db.fetch_file(basename=path)
    
    assert dearch_f is not None, f"File entry with path {path} does not exist in the DB. " \
                                 f"Can't proceed"
    
    
    fire_path = dearch_f.name # getting the file's name from the object dearch
    not_path, path_file = fire_path.split("ftp/", 1) # splitting based on ftp 
    path_file = "ftp/" + path_file
    dearch_fobj = api.fetch_object(firePath=path_file)
    assert dearch_fobj is not None, f"File entry with firePath {path_file} is not archived in FIRE. " \
                            f"Can't proceed"
    
    # download the file
    # construct path to store the dearchived file
    logger.info(f"Downloading file to be dearchived: {path}")
    basename = os.path.basename(path)
    downloaded_path = os.path.join(args.directory, basename)
    api.retrieve_object(firePath=path_file,
                        outfile=downloaded_path)
    logger.info(f"Download completed!")

    if str2bool(args.md5check) is True:
        logger.info("Checking if the md5sum of the retrieved and archived"
                    " object matches")
        f = File(name=downloaded_path)
        assert f.md5 == dearch_fobj.objectMd5, "downloaded file and archived object md5sums do" \
                                               " not match. Can't continue"
        logger.info("md5sums match. Will continue dearchiving FIRE object")

    api.delete_object(fireOid=dearch_fobj.fireOid, dry=str2bool(args.dry))
    # finally, delete de-archived file from RESEQTRACK DB
    db.delete_file(dearch_f, dry=str2bool(args.dry))

db.add_ticket_track(args.ticket, args.directory, dry=str2bool(args.dry))
logger.info('Running completed')
