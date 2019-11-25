#!/usr/bin/env bash

in_file=$1

total=0
for i in `cat $in_file`
do
   num=`javap -classpath ../../jdk/temp:./src/stage/compiled/main:src/stage/compiled/test:./lib/commons-logging.jar:./jspider/lib/junit.jar:.lib/log4j-1.2.8.jar:./lib/unittests.jar:./lib/velocity-dep-1.3.1.jar -c $i | wc -l`
   echo $i  $num
   total=$((total + num))
done
echo $total
