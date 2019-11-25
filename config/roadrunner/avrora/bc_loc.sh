#!/usr/bin/env bash

in_file=$1

total=0
for i in `cat $in_file`
do
   num=`javap -classpath data:../../shared/dacapo-9.12/classes:classes:jar/avrora-cvs-20091224.jar -c $i | wc -l`
   echo $i  $num
   total=$((total + num))
done
echo $total
