#!/usr/bin/env python
import argparse
import os
import logging
import pdb

from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script to generate a new current.tree from files in the RESEQTRACK DB')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('--staging_tree', default='/nfs/1000g-work/G1K/archive_staging/ftp/current.tree',
                    help="File where the new current.tree will be dumped from the RESEQTRACK DB")
parser.add_argument('--prod_tree', default='/nfs/1000g-archive/vol1/ftp/current.tree',
                    help="Current.tree that is in the archive and against which the new current.tree will be compared")
parser.add_argument('--CHANGELOG', default='/nfs/1000g-archive/vol1/ftp/CHANGELOG',
                    help="Path to CHANGELOG file used to record the changes between '--staging_tree' and '--prod_tree'")

# DB and FIRE API connection params
parser.add_argument('--dbpwd', help="Password for MYSQL server. If not provided then it will try to guess "
                                    "the password from the $DBPWD env variable")
parser.add_argument('--dbname', help="Database name. If not provided then it will try to guess the dbname"
                                     " from the $DBNAME env variable")
parser.add_argument('--firepwd', help="FIRE api password. If not provided then it will try to guess the FIRE"
                                      " pwd from the $FIRE_PWD env variable")
parser.add_argument('--log', default='INFO', help="Logging level. i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL")

args = parser.parse_args()

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# set the CONFIG_FILE env variable
os.environ["CONFIG_FILE"] = os.path.abspath(args.settings)

from igsr_archive.current_tree import CurrentTree
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

# connection to Reseqtrack DB
db = DB(pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(pwd=firepwd)

# check if CHANGELOG file is in the DB
chglogFobj = File(
    name=args.CHANGELOG,
    type="CHANGELOG")

rf = db.fetch_file(path=chglogFobj.name)

if rf is None:
    raise Exception(f"CHANGELOG file path: {chglogFobj} does not exist. Can't continue!")

ctree = CurrentTree(db=db,
                    api=api,
                    staging_tree=args.staging_tree,
                    prod_tree=args.prod_tree)

pushed_dict = ctree.run(chlog_fobj=chglogFobj)
