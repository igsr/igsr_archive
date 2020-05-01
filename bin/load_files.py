#!/usr/bin/env python

import argparse
import os
import logging
import re
import pdb
from utils import str2bool

from reseqtrack.db import DB
from file.file import File

logging.basicConfig(level=logging.DEBUG)

# Create logger
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Load file/s in a Reseqtrack database')

parser.add_argument('-s', '--settingsf', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('-t', '--type', required=True, help="This should be a string which will be"
                                                        " associated with all files, for example "
                                                        "FASTQ if you are loading fastq files."
                                                        " There are no restrictions on what this"
                                                        " is other than it should be shorter"
                                                        " than 50 characters, convention normally"
                                                        " has each type in upper case and it is"
                                                        " good if it is in someway informative "
                                                        "about the files loaded.")
parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to load the file without "
                                                 "effectively loading it. True: Perform a dry-run.")
parser.add_argument('-f', '--file', help="Path to file to be stored")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing"
                                                                           " a list of file "
                                                                           "paths, one in each line")
parser.add_argument('--md5_file', type=argparse.FileType('r'), help="File with output from md5sum, in the format:"
                                                                    " <md5checkum>\t<filepath>")


args = parser.parse_args()

logger.info('Running script')

pwd = os.getenv('PWD')
dbname = os.getenv('DBNAME')

assert dbname, "$DBNAME undefined"
assert pwd, "$PWD undefined"

# Class to connect with Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=pwd,
        dbname=dbname)

if args.file:
    logger.info('File provided using -f, --file option')

    f = File(
            path=args.file,
            type=args.type
    )

    db.load_file(f, dry=str2bool(args.dry))
elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')

    for path in args.list_file:
        path = path.rstrip("\n")
        f = File(
            path=path,
            type=args.type
        )

        db.load_file(f, dry=str2bool(args.dry))
elif args.md5_file:
    logger.info('File with <md5sum> <paths> provided using --md5_file option')

    for line in args.md5_file:
        line = line.rstrip("\n")
        md5sum, path = re.split(' +', line)
        f = File(
            path=path,
            type=args.type,
            md5sum=md5sum
        )

        db.load_file(f, dry=str2bool(args.dry))

logger.info('Running completed')
