import csv
import os
import re

filepath = os.path.join("hprc_phase_2_fastq.tsv")
if os.path.isfile(filepath):
    with open('hprc_fastq_clean_sample.tsv','a', newline='', encoding='utf-8') as tsvfile:
        with open(filepath, newline='') as file:  
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                fastq_ftp = row[3]
                sample_name = row[9]
                match = re.search(r'[a-zA-Z]+[0-9]+[a-zA-Z]', sample_name)
                if sample_name == "Human sample from Homo sapiens":
                    continue
                elif match:
                    print(sample_name)
                    sample_name = sample_name[:-1]
                line = f"{sample_name}\t{fastq_ftp}\n"
                tsvfile.write(line)
