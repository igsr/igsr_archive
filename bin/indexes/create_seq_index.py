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
parser.add_argument('--studies', required=True,
                    help="Comma-sep string with ENA study ids. Example: ERP125611,ERP123307")
parser.add_argument('--analysis_group', required=True,
                    help="Analysis group used to identify groups, or sets, of data. Further information may be available with the data collection.")
parser.add_argument('--output', required=True,
                    help="Name of output file with index.")

args = parser.parse_args()

if not os.path.isfile(args.settings):
    raise Exception(f"Config file provided using --settings option({args.settings}) not found!")

# set the CONFIG_FILE env variable
os.environ["CONFIG_FILE"] = os.path.abspath(args.settings)

from igsr_archive.ena.ena_query import ENAportal, ENAbrowser

# Create logger
logger = logging.getLogger(__name__)
logger.info(f"Running {__name__}")

# logging
loglevel = args.log
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(level=numeric_level)

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

ofile = open(args.output, 'w')
ofile.write(header)

# list of attributes to get from ENA
attributes = ['fastq_ftp','fastq_md5','accession', 'secondary_study_accession', 'study_title', 'center_name', 
'submission_accession', 'first_created', 'secondary_sample_accession', 'sample_alias', 'experiment_accession',
'instrument_platform','instrument_model','library_name','run_alias','nominal_length','library_layout', 
'read_count','base_count']

study_lst = args.studies.split(",")

record_lst = []
for study in study_lst:
    eportal = ENAportal(study)

    logger.info('Querying the ENA portal endpoint')

    record_lst_study = eportal.query(fields=",".join(attributes))
    record_lst.append(record_lst_study)
    logger.info(f"Obtained {len(record_lst_study)} records from the ENA portal endpoint for study:{study}")


record_lst = [item for sublist in record_lst for item in sublist]

def get_population(sample_id):
    """
    Function to get the population for 
    a certain sample_id

    It will return None if not defined
    """
    ebrowser = ENAbrowser(acc=sample_id)
    xmld = ebrowser.query()
    attrbs = ebrowser.fetch_attrbs('SAMPLE', xmld, alist=['population'])

    if 'population' in attrbs:
        return attrbs['population']
    else:
        return None

# list of fields to print out in order
fields = ['fastq_ftp','fastq_md5','run_accession', 'secondary_study_accession', 'study_title', 'center_name', 
'submission_accession', 'first_created', 'secondary_sample_accession', 'sample_alias', 'population','experiment_accession',
'instrument_platform','instrument_model','library_name','run_alias','nominal_length','library_layout', 
'paired_fastq','read_count','base_count','analysis_group']

for r in record_lst:
    r.analysis_group = args.analysis_group
    pop = get_population(r.sample_accession)
    if pop is not None:
        r.population = pop
    else:
        logger.info(f"No population defined for {r.sample_accession}. Will be set to 'NA'")
        r.population = 'NA'
    if r.library_layout == 'PAIRED':
        attributes.append('paired_fastq')
        a_list = r.split()
        r1 = a_list[0]
        r2 = a_list[1]
        r1.paired_fastq = r2.fastq_ftp
        r2.paired_fastq = r1.fastq_ftp
        row1 = ""
        row2 = ""
        for attrb in fields:
            if attrb in ['fastq_ftp', 'paired_fastq']:
                # adding 'ftp://' to some attributes
                newattr1 = f"ftp://{getattr(r1, attrb)}"
                newattr2 = f"ftp://{getattr(r2, attrb)}"
                setattr(r1, attrb, newattr1)
                setattr(r2, attrb, newattr2)
            row1 += f"{getattr(r1, attrb)}\t"
            row2 += f"{getattr(r2, attrb)}\t"
        ofile.write(f"{row1}\n{row2}\n")
    elif r.library_layout == 'SINGLE':
        row = ""
        for attrb in fields:
            if attrb == 'fastq_ftp':
                # adding 'ftp://' to some attributes
                newattr = f"ftp://{getattr(r, attrb)}"
                setattr(r, attrb, newattr)
            elif attrb == 'paired_fastq':
                setattr(r, attrb, '')
            row += f"{getattr(r, attrb)}\t"
        ofile.write(f"{row}\n")
    else:
        raise Exception(f"Error: {r.library_layout} is not valid! ")

logger.info("Index creation. Done...")
ofile.close()