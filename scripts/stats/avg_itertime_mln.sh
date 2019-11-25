#!/usr/bin/env bash

stats_dir=$1
file_count=0
for i in $stats_dir/stats*.txt
do
   file_count=$((file_count + 1))
   tail -n +2 $i > tt
   awk '{print $11;}' tt > t
   total=0
   count=0
   while read -r line
   do
      total=$((total + line))
      count=$((count + 1))
   done < t
   avg=$((total/count))
   echo "$avg" >> avg 
done

half=`bc <<< "scale=1; ($file_count/2)"`
median_val=`bc <<< "scale=0; (($half + 0.5)/1)"`
median_iter_time=`sort avg | head -n $median_val | tail -n 1`
echo $median_iter_time
rm -f t tt avg
