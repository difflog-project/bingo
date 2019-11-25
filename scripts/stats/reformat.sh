#!/usr/bin/env bash

stat_dir=$1
tgt_dir=$2

if [ ! -d $tgt_dir ]; then
   mkdir $tgt_dir
fi

for fName in `ls $stat_dir/*stats*`
do
   bname=`basename $fName`
   cat $fName | awk '{print $1 " " $3 " " $4 " " $5;}' > $tgt_dir/$bname 
done
