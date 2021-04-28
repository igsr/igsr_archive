import pytest
import logging
import pdb

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

@pytest.fixture()
def enarecord_obj1():
    """
    Fixture to generate an ENArecord object
    """
    adict = {
        'sample_accession' : 'SAMN00001694', 
        'submitted_ftp' : 'ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_annotatedSV_filtered_nonredundant.smap;ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_assembly.cmap;ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238.YRI.20191223.bionano.DLE1.bnx;ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_annotatedSV.smap;ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_annotatedSV_filtered.smap', 
        'submitted_md5' : '3643c28ec528d89131d6e67dbd65cb47;f70e4ea230e831b37adfd117d2dbe4f1;4ef0ff26df2e3307b4dc4b5da360207f;0df66da20f42096d26b8a540105131a0;f0c98159ccf76cd0a42df5a4130befb3', 
        'secondary_study_accession' : 'ERP124807', 
        'study_title' : 'Bionano data used for the Human Genome Structural Variation Consortium analyses', 
        'enter_name' : 'Bionano Genomics', 
        'secondary_sample_accession' : 'SRS000212', 
        'sample_alias' : 'NA19238'
    }
    erecord = ENArecord(type='ANALYSIS', id='ERZ1669093', **adict)

    return erecord

def test_ENArecord_split_run(enarecord_obj):
    log = logging.getLogger('test_ENArecord_split_run')

    log.debug('Test the split function from ENArecord with a ENArecord of \'RUN\' type')

    a_lst = enarecord_obj.split()

    assert a_lst[0].fastq_ftp == 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_1.fastq.gz'
    assert a_lst[1].fastq_ftp == 'ftp.sra.ebi.ac.uk/vol1/fastq/ERR159/ERR159209/ERR159209_2.fastq.gz'

def test_ENArecord_split_analysis(enarecord_obj1):
    log = logging.getLogger('test_ENArecord_split_run')

    log.debug('Test the split function from ENArecord with a ENArecord of \'RUN\' type')

    a_lst = enarecord_obj1.split(fields=['submitted_ftp', 'submitted_md5'])

    assert a_lst[0].submitted_ftp == 'ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_annotatedSV_filtered_nonredundant.smap'
    assert a_lst[1].submitted_ftp == 'ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_assembly.cmap'
    assert a_lst[2].submitted_ftp == 'ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238.YRI.20191223.bionano.DLE1.bnx'
    assert a_lst[3].submitted_ftp == 'ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_annotatedSV.smap'
    assert a_lst[4].submitted_ftp == 'ftp.sra.ebi.ac.uk/vol1/ERZ166/ERZ1669093/NA19238_YRI_bionano_DLE1_annotatedSV_filtered.smap'

