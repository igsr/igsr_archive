import argparse
import os
import logging
import pdb
import sys
from utils import str2bool
from reseqtrack.db import DB
from fire.api import API

parser = argparse.ArgumentParser(description='Script for interacting with the FIle REplication (FIRE) software. '\
                                              'This script can be used for archiving files in the public '\
                                              'IGSR FTP, it also can be used for moving files within the FTP. '\
                                              'Once a certain file is archived using this script, it will be '\
                                              'accessible from our IGSR public FTP.')

parser.add_argument('-s', '--settingsf', required=True,
                    help="Path to .ini file with settings")

parser.add_argument('--dry', default=True, help="Perform a dry-run and attempt to archive the file without "
                                                "effectively doing it. True: Perform a dry-run")
parser.add_argument('--origin', help="Path to file to be archived. It must exists in the g1k_archive_staging_track DB")
parser.add_argument('--dest', help="Final path of file. It will update the path in the g1k_archive_staging_track DB")

parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing"
                                                                           " a list of target and destination "
                                                                           "paths, one in each line")
parser.add_argument('--type',  help="New file type used in the Reseqtrack DB for archiving the files")
parser.add_argument('--dbpwd', help="Password for MYSQL server. If not provided then it will try to guess"
                                    "the password from the $DBPWD env variable")
parser.add_argument('--dbname', help="Database name. If not provided then it will try to guess"
                                     "the dbname from the $DBNAME env variable")
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

# list of tuples (origin, dest) for files to be archived
files = []

origin_seen = False
if args.origin:
    origin_seen = True
    assert args.dest, "--origin arg defined, --dest arg also needs to be defined"
elif args.dest:
    assert args.origin, "--dest arg defined, --origin arg also needs to be defined"
elif args.list_file:
    logger.info('File with paths provided using -l, --list_file option')

    for line in args.list_file:
        line = line.rstrip("\n")
        try:
            origin, dest = line.split("\t")
            files.append((origin, dest))
        except Exception:
            raise Exception("Format of file provided with --list_file, -l option needs to be:"
                            "<origin>\\t<dest>")

if origin_seen is True:
    logger.info('--origin and --dest args defined')
    files.append((args.origin, args.dest))

# check if user has passed any file
if len(files) == 0:
    logger.info('No file/s provided. Nothing to be done...')
    sys.exit(0)


# connection to Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(settingsf=args.settingsf,
          pwd=firepwd)

for tup in files:
    pdb.set_trace()
    abs_path = os.path.abspath(tup[0])

    # check if 'origin' exists in db and fetch the file
    origin_f = db.fetch_file(path=abs_path)
    assert origin_f is not None, f"File entry with path {abs_path} does not exist in the DB. "\
                                 f"You need to load it first in order to proceed"

    # check if 'origin' already exists in FIRE
    origin_fobj = api.fetch_object(firePath=abs_path)
    if origin_fobj is not None:
        logger.info(f"File provided {abs_path} is in FIRE, it will be moved to {tup[1]}")
        api.update_object(attr_name='firePath',
                          value=tup[1],
                          fireOid=origin_fobj.fireOid,
                          dry=str2bool(args.dry))
    else:
        # now, check if 'dest' exists in db
        assert db.fetch_file(path=tup[1]) is None, f"File entry with path {tup[1]} already exists in the DB."\
                                                   f"It will not continue"

        # push the file to FIRE where tup[1] will the path in the FIRE
        # filesystem
        api.push_object(fileO=origin_f,
                        dry=str2bool(args.dry),
                        fire_path=tup[1])

    # now, modify the file entry in the db and update its name (path)
    db.update_file(attr_name='name',
                   value=tup[1],
                   name=abs_path,
                   dry=str2bool(args.dry))

    if args.type:
        logger.info(f"--type option provided. Its value will be used for updating"
                    f" the file type in {args.dbname}")

        db.update_file(attr_name='type',
                       value=args.type,
                       name=tup[1],
                       dry=str2bool(args.dry))



