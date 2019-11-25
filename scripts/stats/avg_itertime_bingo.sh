#!/usr/bin/env bash

stat_dir=$1
awk '{print $9;}' $stat_dir/stats.txt > t
tail -n +2 t > tt
total=0
count=0
while read -r line
do
   total=$((total + line))
   count=$((count + 1))
done < tt
avg=$((total/count))
echo $avg
rm -f t tt
