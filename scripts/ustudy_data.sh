#!/usr/bin/env bash

# manually produce a file from racePairs_cs.txt that contains all the bugs that you want to 
# include in the user study. Each line in this file must have the format:
# ask FP 14922:org/apache/commons/logging/impl/LogFactoryImpl.java:342  14933:org/apache/commons/logging/impl/LogFactoryImpl.java:372
#
# Next, run the script below to produce the link file names and their associated text.
# $1 is the benchmark directory that contains the xml/html data
# $2 is the name of the above file
# $3 is the name of the output file

bench_dir=$1
in_file=$2
out_file=$3

awk -F'[:| ]' '{print $2 "#" $3 ":" $4 ":" $5 "#" $7 ":" $8 ":" $9}' $in_file > temp 
rm -f $out_file
for i in `cat temp`
do
   truth_val=`echo $i | cut -d '#' -f 1`
   acc1=`echo $i | cut -d '#' -f 2`
   acc2=`echo $i | cut -d '#' -f 3`
   e1=`echo $acc1 | cut -d ':' -f 1`
   name1=`echo $acc1 | cut -d ':' -f 2`
   line1=`echo $acc1 | cut -d ':' -f 3`
   e2=`echo $acc2 | cut -d ':' -f 1`
   name2=`echo $acc2 | cut -d ':' -f 2`
   line2=`echo $acc2 | cut -d ':' -f 3`

   fname1=`basename $name1`
   fname2=`basename $name2`

   key="$e1 $e2"
   linkline=`grep "$key" $bench_dir/EtoTEmap.txt | head -n 1`
   linkf=`echo $linkline | cut -d ':' -f 2` 
   echo "$truth_val   $linkf   $fname1:$line1 and $fname2:$line2" >> $out_file
done
