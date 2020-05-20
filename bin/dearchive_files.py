import argparse
import os
import logging
import pdb
from utils import str2bool
from reseqtrack.db import DB
from fire.api import API
from file.file import File

logging.basicConfig(level=logging.DEBUG)

# Create logger
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Dearchive files from the FIRE archiving system. Dearchive file will be moved'
                                             'to the desired directory')

parser.add_argument('-s', '--settingsf', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('--dry', default=True,
                    help="Perform a dry-run and attempt to dearchive the file without "
                         "effectively doing it. True: Perform a dry-run")
parser.add_argument('--md5check', default=True,
                    help="Check if md5sum of downloaded file and FIRE object matches before dearchiving from FIRE")
parser.add_argument('--file', help="Path to file to be dearchived. It must exists in the g1k_archive_staging_track DB")
parser.add_argument('-l', '--list_file', type=argparse.FileType('r'), help="File containing the paths of the files to"
                                                                           "be dearchived")
parser.add_argument('-d', '--directory', required=True,
                    help="Directory used for storing the dearchived file")
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

# connection to Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=dbpwd,
        dbname=dbname)

# connection to FIRE api
api = API(settingsf=args.settingsf,
          pwd=firepwd)

# list of tuples (origin, dest) for files to be archived
files = []

if args.file:
    logger.info("File provided")
    files.append(args.file)
elif args.list_file:
    logger.info("List of files to dearchive provided")
    for line in args.list_file:
        line = line.rstrip("\n")
        files.append(line)

for path in files:
    dearch_f = db.fetch_file(path=path)
    assert dearch_f is not None, f"File entry with path {path} does not exist in the DB. " \
                                 f"Can't proceed"
    # check if 'path' exists in FIRE
    dearch_fobj = api.fetch_object(firePath=path)
    assert dearch_fobj is not None, f"File entry with firePath {path} is not archived in FIRE. " \
                                    f"Can't proceed"
    # download the file
    # construct path to store the dearchived file
    pdb.set_trace()
    basename = os.path.basename(path)
    downloaded_path = f"{args.directory}/{basename}"
    api.retrieve_object(fireOid=dearch_fobj.fireOid,
                        outfile=downloaded_path)

    if str2bool(args.md5check) is True:
        logger.info("Checking if the md5sum of the retrieved and archived"
                    " object matches")
        f = File(name=downloaded_path)
        assert f.md5 == dearch_fobj.objectMd5, "downloaded file and archived object md5sums do" \
                                               " not match. Can't continue"
        logger.info("md5sums match. Will continue dearchiving FIRE object")

    # delete FIRE object
    api.delete_object(fireOid=dearch_fobj.fireOid, dry=str2bool(args.dry))

