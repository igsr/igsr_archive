import csv
with open("hprc_phase_2.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    new_array = []
    for row in rd:
        sample_names = row[15].split("_")
        for string in sample_names:
            if string.startswith('HG') or string.startswith('NA'):
                row[9] = string.split(".")[0]
        if ";" in row[8]:
            # check if md5sum correspondence is there 
            bam_paths = row[8].split(";")
            bam_md5sums = row[2].split(";")
            for i in range(0,len(bam_paths)):
                read = row
                read[8] = bam_paths[i]
                if len(bam_paths) == len(bam_md5sums):
                    read[2] = bam_md5sums[i]
                else:
                    read[2] = ""
                tmp_read = tuple(read)
                new_array.append(tmp_read)
        elif row[8]:
            new_array.append(row)
    with open('hprc_phase_2_bam.tsv', 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile, delimiter = "\t")
        csvwriter.writerows(new_array)      
              
