grep  "OXFORD" hprc_bam_clean_sample.tsv > oxford_bam.tsv
perl load_index_file.mysql.pl --file oxford_bam.tsv --data_collection hprc2 --data_type alignment --use_column_headers --url_column SUBMITTED_FTP --md5_column SUBMITTED_MD5 --sample_column SAMPLE_TITLE --analysis_group ONT --dbpass thousandgenomes

grep  "PACBIO" hprc_bam_clean_sample.tsv > pacbio_bam.tsv
perl load_index_file.mysql.pl --file pacbio_bam.tsv --data_collection hprc2 --data_type alignment --use_column_headers --url_column SUBMITTED_FTP --sample_column SAMPLE_TITLE --analysis_group sv_smrt --dbpass thousandgenomes

grep  "ILLUMINA" hprc_fastq_clean_sample.tsv > illumina_fastq.tsv
perl load_index_file.mysql.pl --file illumina_fastq.tsv --data_collection hprc2 --data_type sequence --use_column_headers --url_column FASTQ_FTP --sample_column SAMPLE_TITLE --analysis_group novaseq --dbpass thousandgenomes

grep  "PACBIO" hprc_fastq_clean_sample.tsv > pacbio_fastq.tsv
sed -i "/\b\Homo sapiens\b/d" pacbio_fastq.tsv
perl load_index_file.mysql.pl --file pacbio_fastq.tsv --data_collection hprc2 --data_type sequence --use_column_headers --url_column FASTQ_FTP  --sample_column SAMPLE_TITLE --analysis_group sv_smrt --dbpass thousandgenomes

grep  "OXFORD" hprc_fastq_clean_sample.tsv > oxford_fastq.tsv
perl load_index_file.mysql.pl --file data2/oxford_bam.tsv --data_collection hprc2 --data_type alignment --use_column_headers --url_column SUBMITTED_FTP  --sample_column SAMPLE_TITLE --analysis_group ONT --dbpass thousandgenomes
