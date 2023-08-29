#!/usr/bin/env perl

use strict;
use warnings;
use Data::Dumper;
use Net::FTP;

## Check the content of a list of directories against their manifest files
## Looks at FTP dir: vol1/ftp/data_collections/HGSVC3/working/;

die "\nError a file of ftp directories to check is required\n\n" unless defined  $ARGV[0];


my $ftp_dir = "vol1/ftp/data_collections/HGSVC3/working";
my $ftp = Net::FTP->new("ftp.1000genomes.ebi.ac.uk", Debug => 0)|| die "Cannot connect to ftp.1000genomes.ebi.ac.uk: $@";    
$ftp->login("anonymous",'-anonymous@') || die "Cannot login ", $ftp->message; 

open my $dir_list, $ARGV[0] || die "Failed to open dir list $ARGV[0] : $!\n";

# list format - directories to check manifest v content 
# 2021_Hi-C_JAX/	 
# 2021_RNAseq_JAX/
# 20211207_UMIGS_HiFi/GM19434/

while(<$dir_list>){
  chomp;
  my $dir = (split)[0];
  $dir =~ s/\/$//;
  print "Checking $dir\n";
  download($dir);
}

$ftp->quit;

sub download{

  my $dir = shift;
  my %get;

  # back to top to get the right path
  $ftp->cwd() || die "Cannot change to root dir " , $ftp->message;
  $ftp->cwd("$ftp_dir/$dir")  || die "Cannot change project directory to $ftp_dir/$dir ", $ftp->message;

  ## get list of data files per dir
  my $data_file_list = $ftp->dir();

   ## write list of all & download manifest
   open my $out, ">", "$dir\_data_file_list" ||die "Failed to open file to write list of data files for $dir :$!\n";

   foreach my $f (@{$data_file_list}){  
     print $out "$f\n";

     ## some mainfest without manifest in the filename
     if ($f =~ /MANIFEST|20210728_LEE_PacBio_IsoSeq.txt/i){
       my @a = split/\s+/, $f;
       my $mani = pop @a;
       $get{$mani} = 1;
       #print "Saving file: $mani for $dir\n";
     }
   }
   close $out;


   ## download manifest files
   foreach my $mani ( keys %get){  
     $ftp->get( $mani ) || warn "Problem getting $mani\n";
   }


  ## check files in manifest available & get sizes
  open my $size_log, ">$dir\_data_file_sizes" ||die "Failed to open file to write sizes of data files :$!\n";
  foreach my $mani ( keys %get){
    print "starting on manifest  $mani\n";

    open my $filelist, $mani || die "Failed to read manifest $mani :$!\n"; 
    while(<$filelist>){

      my ($file, $size, $md5)  = split, $_;
      ## some manifests include current dir, some don't - remove to standardise
      $file =~ s/^$dir\///;
      $file =~ s/^\.\///;

      my $ret = $ftp->size( $file );	
      if(defined $ret){
         chomp $ret;
      }
      else{
        $ret = 0;
      }
      my $status = "ERROR";
      $status = "OK" if $ret == $size;
      print  $size_log "$mani\t$file\t$ret\t$size\t$status\n";
      }
   } 
   close $size_log;  
   return;
}
