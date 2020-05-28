#!/usr/bin/env python

import argparse
import os
import logging
import pdb
from utils import str2bool

from reseqtrack.db import DB
from file.file import File

parser = argparse.ArgumentParser(description='Delete file/s from a Reseqtrack database')

parser.add_argument('-s', '--settingsf', required=True,
                    help="Path to .ini file with settings")

parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to delete the file without "
                                                "effectively doing it. True: Perform a dry-run")
parser.add_argument('-f', '--file', help="Path to file to be deleted")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing a list of file "
                                                                           "paths, one in each line")
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

if not os.path.isfile(args.settingsf):
    raise Exception(f"Config file provided using --settingsf option({args.settingsf}) not found!")

# Class to connect with Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=pwd,
        dbname=dbname)

if args.file:
    logger.info('File provided using -f, --file option')

    f = File(name=args.file)

    db.delete_file(f, dry=str2bool(args.dry))
elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')

    for path in args.list_file:
        path = path.rstrip("\n")
        f = File(
            name=path,
        )

        db.delete_file(f, dry=str2bool(args.dry))
else:
    logger.info('No file/s provided using the -f or -l options. Nothing to be done...')

logger.info('Running completed')
