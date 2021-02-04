#!/usr/bin/env python
import argparse
import logging
import os

logging.basicConfig(level=logging.DEBUG)

# Create logger
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Fetch a certain FIRE object and its metadata')


parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('--firePath', required=True,
                    help="firePath of object to retrieve")
parser.add_argument('--firepwd', help="FIRE api password. If not provided then it will try to guess"
                                      "the FIRE pwd from the $FIRE_PWD env variable")

logger.info('Running script')

args = parser.parse_args()

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")
# set the CONFIG_FILE env variable
os.environ["CONFIG_FILE"] = os.path.abspath(args.settings)

from igsr_archive.api import API

firepwd = args.firepwd
if args.firepwd is None:
    firepwd = os.getenv('FIRE_PWD')

assert firepwd, "$FIRE_PWD undefined"

# connection to FIRE api
api = API(pwd=firepwd)

fobject = api.fetch_object(firePath=args.firePath)

if fobject is not None:
    print(fobject)