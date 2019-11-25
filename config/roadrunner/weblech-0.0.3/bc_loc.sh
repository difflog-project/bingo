#!/usr/bin/env bash

in_file=$1

total=0
for i in `cat $in_file`
do
   num=`javap -classpath ../../jdk/temp:classes:lib/log4j-1.1.3.jar -c $i | wc -l`
   echo $i  $num
   total=$((total + num))
done
echo $total
