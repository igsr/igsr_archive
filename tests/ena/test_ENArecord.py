import pytest
import logging

from igsr_archive.ena.ena_record import ENArecord

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture()
def enarecord_obj():
    """
    Fixture to generate an ENArecord object
    """
    adict = {
        'fastq_ftp' : 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_1.fastq.gz;ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_2.fastq.gz', 
        'fastq_bytes' : '2506219794;2740965297',
        'fastq_md5' : '4a33dc4f663609989567aa94c79bfcaf;e07a4f1a6dd2712525c0313a2af24fc2', 
        'submitted_ftp' : 'ftp.sra.ebi.ac.uk/vol1/run/ERR159/ERR159209/7899_1#1.bam', 
        'submitted_bytes' : '6117852261', 
        'submitted_md5' : 'db34b279786e60d76ed8773a3976406b', 
        'sra_ftp' : '', 
        'sra_bytes' : '', 
        'sra_md5' : ''
    }
    erecord = ENArecord(type='RUN', id='ERR159209', **adict)

    return erecord


def test_ENArecord_split(enarecord_obj):
    log = logging.getLogger('test_ENArecord_split')

    log.debug('Test the split function from ENArecord')

    rec1, rec2 = enarecord_obj.split()

    assert rec1.fastq_ftp == 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_1.fastq.gz'
    assert rec2.fastq_ftp == 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_2.fastq.gz'

