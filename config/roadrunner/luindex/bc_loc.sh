#!/usr/bin/env bash

in_file=$1

total=0
for i in `cat $in_file`
do
   num=`javap -classpath .:../../shared/dacapo-9.12/classes:classes:jar/lucene-core-2.4.jar:jar/lucene-demos-2.4.jar -c $i | wc -l`
   echo $i  $num
   total=$((total + num))
done
echo $total
