#!/usr/bin/env python
import argparse
import pymysql
import logging
import errno
import os
import pdb

from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script to add the population code for each of the rows in the index.'
                                              'This script will fetch this information from the igsr_website DB')

parser.add_argument('-i', '--input', required=True, help="index file what will be modified")
parser.add_argument('--host', required=True, help="mysql host name")
parser.add_argument('-u','--user', required=True, help="mysql user name")
parser.add_argument('-d','--dbname', required=True, help="database name")
parser.add_argument('-P','--port', required=True, help="port number")
parser.add_argument('--output', required=True, help="Name of output file with index.")

parser.add_argument('--log', default='INFO', help="Logging level. i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL")

args = parser.parse_args()

# Create logger
logger = logging.getLogger(__name__)
logger.info(f"Running {__name__}")

# logging
loglevel = args.log
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(level=numeric_level)

def set_conn():
    """
    Function that will set a connection
    to the MySQL database

    Returns
    -------
    Connection object
    """

    logger.debug('Setting connection...')

    conn = pymysql.connect(host=args.host,
                           user=args.user,
                           db=args.dbname,
                           port=int(args.port))

    logger.debug('Connection successful!')

    return conn

def get_pop_code(s_name):
    """
    Function to get the population code from 
    args.dbname for a certain sample name

    Params
    ------
    s_name : str
             sample name
    
    Returns
    -------
    str : population code
    """
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = "select distinct population.code from sample, dc_sample_pop_assign, population where sample.name= %s and sample.sample_id=dc_sample_pop_assign.sample_id and dc_sample_pop_assign.population_id=population.population_id"
    cursor.execute(query, [s_name])
    try:
        result_set = cursor.fetchall()
        if not result_set:
            logger.info(f"No population code retrieved from DB using sample name:{s_name}")
            return 'NA'
        for row in result_set:
            return row['code']
        cursor.close()
        conn.commit()
    except pymysql.Error as e:
        logger.info("Exception occurred", exc_info=True)
        # Rollback in case there is any error
        conn.rollback()

logger.info(f"Run started!")

conn = set_conn()

ofile = open(args.output, 'w')

try:
    f = open(args.input, 'r')
except OSError as err:
    if err.errno == errno.ENOENT:
        print(f"[Errno {err.errno} ({errno.errorcode[err.errno]})] {os.strerror(err.errno)}")
    elif err.errno == errno.EACCES:
        print(f"[Errno {err.errno} ({errno.errorcode[err.errno]})] {os.strerror(err.errno)}")
else:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith('#'):
            ofile.write(line+"\n")
            continue
        else:
            elms = line.split('\t')
       #     sample_name = elms[9]
            # remove this line as sample name should not have this format
            sample_name = elms[9].split('_')[0]
            code = get_pop_code(sample_name)
            elms[10] = code
            ofile.write("\t".join(elms)+"\n")
finally:
    f.close()
    logger.info(f"Run completed!")
