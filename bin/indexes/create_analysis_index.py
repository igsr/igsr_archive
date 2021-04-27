"""
submitted_ftp, submitted_md5, analysis_accession, secondary_study_accession, study_title, center_name,XML(<XREF_LINK>
<DB>ENA-SUBMISSION</DB>
<ID>ERA3062116</ID>
</XREF_LINK>),first_public,secondary_sample_accession,sample_alias,population,<ANALYSIS_TYPE>
<GENOME_MAP>
<PLATFORM>BioNano</PLATFORM>
</GENOME_MAP>,<ANALYSIS_TYPE>
<GENOME_MAP>
<PROGRAM>Saphyr</PROGRAM>
</GENOME_MAP>
"""
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
            "##ANALYSIS_ID=SRA/ERA analysis accession\n"
            "##STUDY_ID=SRA/ERA study accession\n"
            "##STUDY_NAME=Name of study\n"
            "##CENTER_NAME=Submission centre name\n"
            "##SUBMISSION_ID=SRA/ERA submission accession\n"
            "##SUBMISSION_DATE=Date sequence submitted, YYYY-MM-DD\n"
            "##SAMPLE_ID=SRA/ERA sample accession\n"
            "##SAMPLE_NAME=Sample name\n"
            "##POPULATION=Sample population. Further information may be available with the data collection.\n"
            "##PLATFORM=Type of machine\n"
            "##PROGRAM=Analysis software\n"
            "#ENA_FILE_PATH\tMD5SUM\tANALYSIS_ID\tSTUDY_ID\tSTUDY_NAME\tCENTER_NAME\tSUBMISSION_ID\tSUBMISSION_DATE\tSAMPLE_ID\tSAMPLE_NAME\tPOPULATION\tPLATFORM\tPROGRAM\n")
    
    header = filedate+header
    return header

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

def get_metadata(id):
    """
    Get the analyis-related metadata from XML dict
    obtained from the ENA browser API

    Parameter
    ---------
    id : accession id
    """
    pdb.set_trace()
    ebrowser = ENAbrowser(acc=id)
    xmld = ebrowser.query()

    xrefs = ebrowser.fetch_xrefs(type='ANALYSIS', xml_dict=xmld)

    metadata_d = {
        'program' : xmld['ANALYSIS_SET']['ANALYSIS']['ANALYSIS_TYPE']['GENOME_MAP']['PROGRAM'],
        'platform' : xmld['ANALYSIS_SET']['ANALYSIS']['ANALYSIS_TYPE']['GENOME_MAP']['PLATFORM']

    }

header=generate_header()

ofile = open(args.output, 'w')
ofile.write(header)

# list of attributes to get from ENA portal
attributes = ['submitted_ftp', 'submitted_md5', 'analysis_accession', 'secondary_study_accession', 'study_title', 'center_name',
'first_public', 'secondary_sample_accession', 'sample_alias']
study_lst = args.studies.split(",")

record_lst = []
for study in study_lst:
    eportal = ENAportal(study)

    logger.info('Querying the ENA portal endpoint')
    record_lst_study = eportal.query(q_type='analysis', fields=",".join(attributes))
    record_lst.append(record_lst_study)
    logger.info(f"Obtained {len(record_lst_study)} records from the ENA portal endpoint for study:{study}")

record_lst = [item for sublist in record_lst for item in sublist]

for r in record_lst:
    print("h")
    get_metadata(id=r.accession)
    print("h\n")

print("hello")