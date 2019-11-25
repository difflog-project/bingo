#!/bin/bash

total_count=0
for d in `ls`
do
  count=0
  for c in `find $d -name "*.class"`
  do
    name="${c%.*}"
#    echo $name
    l=`javap -c $name | wc -l`
    count=`expr $count + $l`
  done
  total_count=`expr $total_count + $count`
  echo $name " : " $count
done
echo "total : " $total_count
