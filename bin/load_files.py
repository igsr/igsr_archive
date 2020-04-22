#!/usr/bin/env python

import argparse
import os

from reseqtrack.db import DB
from file.file import File

parser = argparse.ArgumentParser(description='Load file/s in a Reseqtrack database')

parser.add_argument('-s', '--settingsf', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('-f', '--file', help="Path to file to be stored")
parser.add_argument('-l', '--list_file', help="File containing"
                                              " a list of file "
                                              "paths, one in each line")
parser.add_argument('--md5_file', help="File with output from md5sum, in the format: <md5checkum>\t<filepath>")

args = parser.parse_args()

pwd = os.getenv('PWD')
dbname = os.getenv('DBNAME')

assert dbname, "$DBNAME undefined"
assert pwd, "$PWD undefined"

# Class to connect with Reseqtrack DB
db = DB(settingf=args.settingsf,
        pwd=pwd,
        dbname=dbname)

f = File(
        path=args.f,
        type="TYPE_F"
    )