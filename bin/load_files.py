#!/usr/bin/env python

import argparse
import os
import sys
import logging
import pdb
import re
from igsr_archive.utils import str2bool

from igsr_archive.db import DB
from igsr_archive.file import File

parser = argparse.ArgumentParser(description='Load file/s in a Reseqtrack database')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('-t', '--type', help="This is a string which will be associated with the different type of files, for example "
                                         "FASTQ if you are loading fastq files. There are no restrictions on what this is other than "
                                         "it should be shorter than 50 characters, convention normally has each type in upper case and "
                                         "it is good if it is in someway informative about the files loaded. If not provided then "
                                         "it will guessed by comparing its extension with the rules provided in the 'file_type_rules' "
                                         "section in the settings.ini file")
parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to load the file without "
                                                 "effectively loading it. True: Perform a dry-run.")
parser.add_argument('-f', '--file', help="Path to file to be stored")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing a list of file "
                                                                           "paths to be loaded, one in each line")
parser.add_argument('--md5_file', type=argparse.FileType('r'), help="File with output from md5sum, in the format:"
                                                                    " <md5checksum>  <filepath>")

parser.add_argument('--unique', default=True, help="Check if a file with either the same basename (or path) does "
                                                   "already exist in the DB. True: Will not load the file "
                                                   "if name or path already exists")
parser.add_argument('-p', '--pwd', help="Password for MYSQL server. If not provided then it will try to guess"
                                        "the password from the $PASSWORD env variable")
parser.add_argument('-d', '--dbname', help="Database name. If not provided then it will try to guess"
                                           "the dbname from the $DBNAME env variable")
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

pwd = args.pwd
if args.pwd is None:
    pwd = os.getenv('DBPWD')

dbname = args.dbname
if args.dbname is None:
    dbname = os.getenv('DBNAME')

if dbname is None:
    raise Exception("$DBNAME undefined. You need either to pass the name of the "
                    "RESEQTRACK database using the --dbname option or set a $DBNAME "
                    "environment variable before running this script!")
if pwd is None:
    raise Exception("$DBPWD undefined. You need either to pass the password of the MYSQL "
                    "server containing the RESEQTRACK database using the --pwd option or set a $DBPWD environment "
                    "variable before running this script!")

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# Class to connect with Reseqtrack DB
db = DB(settingsf=args.settings,
        pwd=pwd,
        dbname=dbname)

# list with paths to be loaded
files = []
if args.file:
    logger.info('File provided using -f, --file option')

    if args.type is not None:
        logger.debug('Type provided using -t, --type option')
        f = File(name=args.file,
                 type=args.type)
    else:
        logger.debug('No file type provided using -t, --type option')
        logger.debug('File type will be guessed from its file extension')
        f = File(name=args.file,
                 settingsf=args.settings)
        ftype = f.guess_type()
        f.type = ftype
    files.append(f)

elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')
  #  pdb.set_trace()
    for path in args.list_file:
        path = path.rstrip("\n")
        cols = re.split(' +', path)
        if len(cols) > 1:
            raise Exception(f"Path provided {path} is not correct. "
                            f"Check format")

        if args.type is not None:
            logger.debug('Type provided using -t, --type option')
            f = File(name=path,
                     type=args.type)
        else:
            logger.debug('No file type provided using -t, --type option')
            logger.debug('File type will be guessed from its file extension')
            f = File(name=path,
                     settingsf=args.settings)
            ftype = f.guess_type()
            f.type = ftype
        files.append(f)
elif args.md5_file:
    logger.info('File with <md5sum> <paths> provided using --md5_file option')

    for line in args.md5_file:
        line = line.rstrip("\n")
        cols = re.split(' +', line)
        if len (cols) != 2:
            raise Exception("Incorrect number of columns in file used for --md5_file. "
                            "Check format. It should be: <md5sum>  <path>. First and second column should be"
                            "separated by exactly 2 whitespaces.")
        md5sum, path = (cols[0], cols[1])
        if args.type is not None:
            logger.debug('Type provided using -t, --type option')
            f = File(name=path,
                     type=args.type,
                     md5=md5sum)
        else:
            logger.debug('No file type provided using -t, --type option')
            logger.debug('File type will be deduced using file extension')
            f = File(name=path,
                     settingsf=args.settings,
                     md5=md5sum)
            ftype = f.guess_type()
            f.type = ftype
        files.append(f)
else:
    raise Exception("You need to provide the file/s to be loaded using either "
                    "the -f, -l or --md5_file options")

for f in files:
    if f.check_if_exists() is False:
        print(f"There was an error when trying to load: {f.name}. Wrong file path")
        sys.exit(1)
    if str2bool(args.unique) is True:
        # get basename and check if it already exists in DB
        basename = os.path.basename(f.name)
        rf = db.fetch_file(basename=basename)
        assert rf is None, f"A file with the name '{basename}' already exists in the DB. You need to change the name " \
                           f"'{basename}' so it is unique."

    db.load_file(f, dry=str2bool(args.dry))

logger.info('Running completed')
