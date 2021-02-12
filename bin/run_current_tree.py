#!/usr/bin/env python
import argparse
import os
import logging
import pdb
import re

from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script to generate a new current.tree from files in the RESEQTRACK DB')

parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('--CHANGELOG', default='/nfs/1000g-archive/vol1/ftp/CHANGELOG',
                    help="Path to CHANGELOG file used to record the changes between '--staging_tree' and '--prod_tree'")
parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to run the current.tree process without "
                                                "pushing any object to FIRE or modifying the DB."
                                                "Default: True")

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

# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

from igsr_archive.current_tree import CurrentTree
from igsr_archive.db import DB
from igsr_archive.api import API
from igsr_archive.utils import str2bool

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

prod_tree = f"{settingsO.get('ftp', 'ftp_mount')}/{settingsO.get('ctree', 'ctree_fpath')}/current.tree"
prod_tree = prod_tree.replace('//','/')
staging_tree = f"{settingsO.get('ctree', 'temp')}/current.tree"
staging_tree = staging_tree.replace('//','/')

# check if prod_tree is in DB and in FIRE
ct = db.fetch_file(path=prod_tree)
if ct is None:
    raise Exception(f"Prod_tree: {prod_tree} does not exist in the DB. Can't continue!")
ct_fpath = re.sub(settingsO.get('ftp', 'ftp_mount') + "/", '', prod_tree)
ct_fobj = api.fetch_object(firePath=ct_fpath)
if ct_fobj is None:
    raise Exception(f"Prod_tree file path: {prod_tree} is not archived in FIRE. Can't continue!")

# check if CHANGELOG path is in the DB
rf = db.fetch_file(path=args.CHANGELOG)
if rf is None:
    raise Exception(f"CHANGELOG file path: {args.CHANGELOG} does not exist. Can't continue!")

# make a copy of the chglogFobj file that will be modified, as the
# version that is archived is read-only
changelog_fpath = re.sub(settingsO.get('ftp', 'ftp_mount') + "/", '', args.CHANGELOG)
# get fireOid for chglogFobj file
f_obj = api.fetch_object(firePath=changelog_fpath)
if f_obj is None:
    raise Exception(f"CHANGELOG file path: {args.CHANGELOG} is not archived in FIRE. Can't continue!")

chlogl_path = f"{settingsO.get('ctree', 'temp')}/{os.path.basename(args.CHANGELOG)}"
api.retrieve_object(fireOid=f_obj.fireOid, outfile=chlogl_path)

ctree = CurrentTree(db=db,
                    api=api,
                    staging_tree=staging_tree,
                    prod_tree=prod_tree)

pushed_dict = ctree.run(chlog_f=chlogl_path,
                        dry=str2bool(args.dry))

if pushed_dict:
    logger.info(f"The following changelog_details_* files have geen generated and pushed to archive:")
    chglog_details_str = "\n".join(pushed_dict['chlog_details'])
    logger.info(f"{chglog_details_str}\n")
    logger.info(f"The current.tree file has been pushed to archive with FIRE path {pushed_dict['ctree_firepath']}")
    logger.info(f"The CHANGELOG file has been pushed to archive with FIRE path {pushed_dict['chlog_firepath']}")

    # delete temp files
    os.remove(chlogl_path)
    os.remove(staging_tree)
    for f in pushed_dict['chlog_details']:
        new_p = "{0}/{1}".format(settingsO.get('ctree', 'temp'), os.path.basename(f))
        os.remove(new_p)