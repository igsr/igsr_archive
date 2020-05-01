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

parser = argparse.ArgumentParser(description='Delete file/s from a Reseqtrack database')

parser.add_argument('-s', '--settingsf', required=True,
                    help="Path to .ini file with settings")

parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to delete the file without "
                                                 "effectively doing it. True: Perform a dry-run.")
parser.add_argument('-f', '--file', help="Path to file to be deleted")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing"
                                                                           " a list of file "
                                                                           "paths, one in each line")

args = parser.parse_args()

logger.info('Running script')

pwd = os.getenv('PASSWORD')
dbname = os.getenv('DBNAME')

assert dbname, "$DBNAME undefined"
assert pwd, "$PASSWORD undefined"

# Class to connect with Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=pwd,
        dbname=dbname)

if args.file:
    pdb.set_trace()
    logger.info('File provided using -f, --file option')

    f = File(
            path=args.file
    )

    db.delete_file(f, dry=str2bool(args.dry))
elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')

    for path in args.list_file:
        path = path.rstrip("\n")
        f = File(
            path=path,
        )

        db.delete_file(f, dry=str2bool(args.dry))

logger.info('Running completed')
