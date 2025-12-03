import csv
import os
from urllib.parse import urlparse
from ftplib import FTP

ftp_url = "ftp://ftp.ncbi.nlm.nih.gov/"
http_url = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/"
parsed = urlparse(ftp_url)
ftp = FTP(parsed.hostname)
ftp.login() 
analysis_method = "HiFi"


with open('assemblies_list.tsv', newline='') as file:
    reader = csv.reader(file, delimiter='\t')
    with open("assembly.index", 'a', newline='', encoding='utf-8') as tsvfile:
        for row in reader:
            sample_name = row[0]
            gca_accession = row[8]
            
            gca_p1 = gca_accession[4:7]
            gca_p2 = gca_accession[7:10]
            gca_p3 = gca_accession[10:13]
            if gca_p1.isdigit():
                folder_path = os.path.join("/genomes/all/GCA/", gca_p1, gca_p2, gca_p3)
                ftp.cwd(folder_path)
                fasta_folder = ftp.nlst()[0]
                fasta_basename = f"{fasta_folder}_genomic.fna.gz"
                fasta_file = os.path.join(http_url, gca_p1, gca_p2, gca_p3,fasta_folder,fasta_basename)
                line = f"{sample_name}\t{fasta_file}\t{analysis_method}\n"
                tsvfile.write(line)
                
           
        