#!/usr/bin/env bash

# This script takes the dir containing outputs of RR runs and extracts unique races from them.
# args:
#  run_dir  : the directory that contains the output files of one or more RR runs
#  op_file  : the file in which the extracted races are printed.

run_dir=$1
op_file=$2

scr_path=`dirname $0`
rm -f $run_dir/combined_out
rm -f $run_dir/combined_out_filt

for i in `ls $run_dir/*`
do
  cat $i >> $run_dir/combined_out
done

# RR starts all lines reporting dataraces with "##" 
# This filtering below is required because sometimes applications spew output that
# contain characters that crash extract.py when it is  reading the input file.
# Example of crash and error:
#    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa0 in position 113: invalid start byte 
grep "##" $run_dir/combined_out > $run_dir/combined_out_filt
$scr_path/extract.py < $run_dir/combined_out_filt > $op_file
