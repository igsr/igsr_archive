import argparse
import os
import logging
import pdb
from utils import str2bool
from reseqtrack.db import DB
from fire.api import API

logging.basicConfig(level=logging.DEBUG)

# Create logger
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Archive files in the FIRE archiving system so they can be'
                                             'accessed in the public FTP')

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

args = parser.parse_args()

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

assert firepwd, "$FIRE_PWD undefined"
assert dbname, "$DBNAME undefined"
assert dbpwd, "$DBPWD undefined"

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

# connection to Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(settingsf=args.settingsf,
          pwd=firepwd)
pdb.set_trace()
for tup in files:
    # check if 'origin' exists in db and fetch the file
    origin_f = db.fetch_file(path=tup[0])
    assert origin_f is not None, f"File entry with path {tup[0]} does not exist in the DB. "\
                                 f"You need to load it first in order to proceed"

    # check if 'origin' already exists in FIRE
    origin_fobj = api.fetch_object(firePath=tup[0])
    if origin_fobj is not None:
        logger.info(f"File provided {tup[0]} is in FIRE, it will be moved to {tup[1]}")
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
                   name=tup[0],
                   dry=str2bool(args.dry))

    if args.type:
        logger.info(f"--type option provided. Its value will be used for updating"
                    f" the file type in {args.dbname}")

        db.update_file(attr_name='type',
                       value=args.type,
                       name=tup[1],
                       dry=str2bool(args.dry))



