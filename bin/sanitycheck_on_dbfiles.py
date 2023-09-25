#!/usr/bin/env python
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
staging_path = '/nfs/1000g-work/G1K/archive_staging/' 
archive_path ='/nfs/1000g-archive/vol1/'
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

# connection to Reseqtrack DB
db = DB(pwd=dbpwd,
        dbname=dbname)

if args.directory:
    #Files fetched in staging
    #Files fetched from archive
    basename = os.path.basename(args.directory.rstrip("/"))
    staging_list = db.fetch_files_by_pattern(pattern=f"{staging_path}%{basename}")
    len_staging_list = 0
    len_archive_list = 0
    if staging_list:
        with open(f"{basename}_staging_files", 'w') as sf:
            for staging_file in staging_list:
                sf.write(f"{staging_file}\n")
        len_staging_list = len(staging_list)
    archive_list = db.fetch_files_by_pattern(pattern=f"{archive_path}%{basename}")
    if archive_list:
        with open(f"{basename}_archive_files", 'w') as af:
            for archive_file in archive_list:
                af.write(f"{archive_file}\n")
        len_archive_list = len(archive_list)
    logger.info(f"Number of files returned in staging: {len_staging_list}")
    logger.info(f"Number of files returned in archive: {len_archive_list}")
    if staging_list and archive_list:
        logger.info(f"Staging files in {basename}_staging_files are not archived")

else:
    if firepwd is None:
        raise Exception("$FIRE_PWD undefined. You need either to pass the FIRE API password using the --firepwd option"
                    " or set a $FIRE_PWD environment variable before running this script!")
    # connection to FIRE api
    api = API(pwd=firepwd)
    logger.info("No specific directory specified. Check all the files on ftp")
    flist = db.fetch_files_by_pattern(pattern='/nfs/1000g-archive/vol1/ftp/')
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
