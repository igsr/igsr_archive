#!/usr/bin/env python
import argparse
import logging
import pdb
import os

from datetime import datetime
from configparser import ConfigParser

parser = argparse.ArgumentParser(description='Script to generate a sequence index using the ENA metadata.')

parser.add_argument('--log', default='INFO', help="Logging level. i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL")
parser.add_argument('-s', '--settings', required=True,
                    help="Path to .ini file with settings")
parser.add_argument('--study', required=True,
                    help="ENA study id. Example: ERP125611")

args = parser.parse_args()

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# set the CONFIG_FILE env variable
os.environ["CONFIG_FILE"] = os.path.abspath(args.settings)
# Parse config file
settingsO = ConfigParser()
settingsO.read(args.settings)

def generate_header():
    """
    Function to generate the header of the index file
    """
    now = datetime.now()
    filedate = now.strftime("##FileDate=%Y%m%d\n")
    header = ("##ENA_FILE_PATH=path to ENA file on ENA ftp site\n"
              "##MD5=md5sum of file\n"
              "##RUN_ID=SRA/ERA run accession\n"
              "##STUDY_ID=SRA/ERA study accession\n"
              "##STUDY_NAME=Name of study\n"
              "##CENTER_NAME=Submission centre name\n"
              "##SUBMISSION_ID=SRA/ERA submission accession\n"
              "##SUBMISSION_DATE=Date sequence submitted, YYYY-MM-DD\n"
              "##SAMPLE_ID=SRA/ERA sample accession\n"
              "##SAMPLE_NAME=Sample name\n"
              "##POPULATION=Sample population. Further information may be available with the data collection.\n"
              "##EXPERIMENT_ID=Experiment accession\n"
              "##INSTRUMENT_PLATFORM=Type of sequencing machine\n"
              "##INSTRUMENT_MODEL=Model of sequencing machine\n"
              "##LIBRARY_NAME=Library name\n"
              "##RUN_NAME=Name of machine run\n"
              "##INSERT_SIZE=Submitter specifed insert size/paired nominal length\n"
              "##LIBRARY_LAYOUT=Library layout, this can be either PAIRED or SINGLE\n"
              "##PAIRED_FASTQ=Name of mate pair file if exists (Runs with failed mates will have a library layout of PAIRED but no paired fastq file)\n"
              "##READ_COUNT=Read count for the file\n"
              "##BASE_COUNT=Basepair count for the file\n"
              "##ANALYSIS_GROUP=Analysis group is used to identify groups, or sets, of data. Further information may be available with the data collection.\n"
              "#ENA_FILE_PATH	MD5SUM	RUN_ID	STUDY_ID	STUDY_NAME	CENTER_NAME	SUBMISSION_ID	SUBMISSION_DATE	SAMPLE_ID	SAMPLE_NAME	POPULATION"\
              "EXPERIMENT_ID	INSTRUMENT_PLATFORM	INSTRUMENT_MODEL	LIBRARY_NAME	RUN_NAME	INSERT_SIZE	LIBRARY_LAYOUT	PAIRED_FASTQ	READ_COUNT	BASE_COUNT	ANALYSIS_GROUP\n")
    
    header = filedate+header
    return header

header=generate_header()
pdb.set_trace()
