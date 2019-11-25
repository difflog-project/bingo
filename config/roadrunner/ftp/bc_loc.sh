#!/usr/bin/env bash

in_file=$1

total=0
for i in `cat $in_file`
do
   num=`javap -classpath ../../jdk/temp:./classes/:./lib/commons-logging-1.0.3.jar:./lib/log4j-1.2.12.jar -c $i | wc -l`
   echo $i  $num
   total=$((total + num))
done
echo $total
