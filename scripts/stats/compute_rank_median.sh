#!/usr/bin/env bash

stat_dir=$1
auc=$2
total_alarms=$3
true_alarms=$4

rm -f t
count=0
ignore=0
file_count=0
for fName in `ls $stat_dir/*stats*`
do
   num_true=`grep TrueGround $fName | wc -l`
   file_count=$((file_count + 1))
   if [[ "$num_true" != "" && $num_true -eq $true_alarms ]]; then
      num_true_h=`grep "TrueGround" $fName | tail -n 1 | awk '{print$3;}'`
      num_false_h=`grep "TrueGround" $fName | tail -n 1 | awk '{print$4;}'`
      rank_h=$((num_true_h + num_false_h))
      count=$((count + 1))
      echo $rank_h >> t
   else
      ignore=$((ignore + 1))
   fi
done

if [ $file_count -eq $ignore ]; then
   echo "timeout"
   exit 0
fi

half=`bc <<< "scale=1; ($count/2)"`
median_val=`bc <<< "scale=0; (($half + 0.5)/1)"`
echo "Median index: " $median_val

sort -n t > t_sort
median_rank_h=`head -n $median_val t_sort | tail -n 1`
rm -f t t_sort

echo "Num TP: " $num_true_h
val=`bc <<< "scale=1; ($num_true_h - ($num_true_h/10))"`
ninety_per=`bc <<< "scale=0; (($val + 0.5)/1)"`
echo "Ninetieth percentile: " $ninety_per

for fName in `ls $stat_dir/*stats*`
do
   num_true=`grep TrueGround $fName | wc -l`
   if [[ "$num_true" != "" && $num_true -eq $true_alarms ]]; then
      num_true_n=`grep "TrueGround" $fName | head -n $ninety_per | tail -n 1 | awk '{print$3;}'`
      num_false_n=`grep "TrueGround" $fName | head -n $ninety_per | tail -n 1 | awk '{print$4;}'`
      rank_n=$((num_true_n + num_false_n))
   echo $rank_n >> t
   fi
done
sort -n t > t_sort
median_rank_n=`head -n $median_val t_sort | tail -n 1`
rm -f t t_sort

echo "Median rank 100%:" $median_rank_h   
echo "Median rank 90%:" $median_rank_n   

rm -f a
if [[ $auc == "auc" ]]
then
   for fName in `ls $stat_dir/*stats*`
   do
      num_true=`grep TrueGround $fName | wc -l`
      if [[ "$num_true" != "" && $num_true -eq $true_alarms ]]; then
         $BASE_DIR/scripts/stats/auc.py $fName t $total_alarms > tt 2>&1      
         grep AUC tt | awk '{print $2;}' >> a
      fi
   done
   sort -n a > a_sort
   median_auc=`head -n $median_val a_sort | tail -n 1`
   rounded_median=`bc <<< "scale=2; (($median_auc + 0.005)/1)"`
   rm -f tt t a a_sort t.png
   echo "Median AUC:" $rounded_median   
fi
