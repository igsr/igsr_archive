#!/usr/bin/env python

import argparse
import os
import re
import logging
from igsr_archive.utils import str2bool
from igsr_archive.api import API
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='This script is the simplest way of deleting file/s from FIRE.'
                                             'It is different from dearchive_files.py as it does not require'
                                             'that the file to be removed is tracked in the DB')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('-f', '--file', help="FIRE path of the object to be removed")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing the FIRE paths of the objects to"
                                                                           "be removed")
parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to delte the file without "
                                                "effectively doing it. True: Perform a dry-run")
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

firepwd = args.firepwd
if args.firepwd is None:
    firepwd = os.getenv('FIRE_PWD')

assert firepwd, "$FIRE_PWD undefined"

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

# connection to FIRE api
api = API(settingsf=args.settings,
          pwd=firepwd)

# list of tuples (origin, dest) for files to be archived
files = []

if args.file:
    logger.info("File provided")
    files.append(args.file)
elif args.list_file:
    logger.info("List of files to remove provided")
    for line in args.list_file:
        line = line.rstrip("\n")
        files.append(line)

for fire_path in files:
    # check if 'path' exists in FIRE
    dearch_fobj = api.fetch_object(firePath=fire_path)
    assert dearch_fobj is not None, f"File entry with firePath {fire_path} is not archived in FIRE. " \
                                    f"Can't proceed"
    # delete FIRE object
    api.delete_object(fireOid=dearch_fobj.fireOid, dry=str2bool(args.dry))

