import csv
with open("hprc_phase_2.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    new_array = []
    for row in rd:
        sample_names = row[15].split("_")
        for string in sample_names:
            if string.startswith('HG') or string.startswith('NA'):
                row[9] = string.split(".")[0]
        if ";" in row[3]:
            # check if md5sum correspondence is there 
            fastq_paths = row[3].split(";")
            fastq_md5sums = row[1].split(";")
            for i in range(0,len(fastq_paths)):
                read = row
                read[3] = fastq_paths[i]
                if len(fastq_paths) == len(fastq_md5sums):
                    read[1] = fastq_md5sums[i]
                else:
                    read[1] = ""
                tmp_read = tuple(read)
                new_array.append(tmp_read)
        elif row[3]:
            new_array.append(row)
    with open('hprc_phase_2_fastq.tsv', 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile, delimiter = "\t")
        csvwriter.writerows(new_array)      
              
