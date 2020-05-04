import argparse
import os
import logging
import pdb
from utils import str2bool
from reseqtrack.db import DB

from file.file import File

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
args = parser.parse_args()

logger.info('Running script')

pwd = os.getenv('PASSWORD')
dbname = os.getenv('DBNAME')

assert dbname, "$DBNAME undefined"
assert pwd, "$PASSWORD undefined"

# tuple (origin, dest) for files to be archived
files = ()

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
            files = (origin, dest)
        except Exception:
            raise Exception("Format of file provided with --list_file, -l option needs to be:"
                            "<origin>\\t<dest>")
        print("h\n")


if origin_seen is True:
    logger.info('--origin and --dest args defined')
    files = (args.origin, args.dest)

# establish connection with DB
pwd = os.getenv('DBPWD')
dbname = os.getenv('DBNAME')

assert dbname, "$DBNAME undefined"
assert pwd, "$PWD undefined"

db = DB(settingf=args.settingsf,
        pwd=pwd,
        dbname=dbname)



for tup in files:




