import argparse
import os
import pdb
import logging
import re

from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script to check if all files in the DB considered to be archived in FIRE '
                                             'are actually in FIRE')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")

# DB and FIRE API connection params
parser.add_argument('--dbpwd', help="Password for MYSQL server. If not provided then it will try to guess "
                                    "the password from the $DBPWD env variable")
parser.add_argument('--dbname', help="Database name. If not provided then it will try to guess the dbname"
                                     " from the $DBNAME env variable")
parser.add_argument('--firepwd', help="FIRE api password. If not provided then it will try to guess the FIRE"
                                      " pwd from the $FIRE_PWD env variable")
parser.add_argument('--directory', help="Directory to compare staging and archive" )
parser.add_argument('--log', default='INFO', help="Logging level. i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL")


args = parser.parse_args()

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")
# set the CONFIG_FILE env variable
os.environ["CONFIG_FILE"] = os.path.abspath(args.settings)

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

from igsr_archive.db import DB
from igsr_archive.api import API

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

flist = db.fetch_files_by_pattern(pattern='/nfs/1000g-archive/vol1/ftp/')

if args.directory:
    flist = db.fetch_files_by_pattern(pattern=args.directory)

logger.info(f"Number of files returned with this pattern {len(flist)}")

tot_counter = 0
count = 0
for p in flist:
    if count == 100:
        logger.info(f"{tot_counter} lines processed!")
        count = 0
    tot_counter += 1
    count += 1

    if settingsO.get('ftp', 'ftp_mount') in p:
        fire_path = re.sub(settingsO.get('ftp', 'ftp_mount') + "/", '', p)
        fire_obj = None
        fire_obj = api.fetch_object(firePath=fire_path)
        if fire_obj is None:
            print(f"ERROR: File witH PATH {p} is not archived in FIRE")
