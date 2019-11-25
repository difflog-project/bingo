#!/usr/bin/env bash

app=$1

python3 $BASE_DIR/scripts/roadrunner/loc2tuple.py $app.fs.loc chord_output_mln-datarace-oracle-thresc/racePairs_cs.txt t
sort t | uniq > $app.fs
rm -f t

python3 $BASE_DIR/scripts/roadrunner/tuple2loc.py $app.gt chord_output_mln-datarace-oracle-unsound-thresc/racePairs_cs.txt t
python3 $BASE_DIR/scripts/roadrunner/loc2tuple.py t chord_output_mln-datarace-oracle-unsound-thresc/racePairs_cs.txt tt
sort tt | uniq > gt_in_unsound 
rm -f t tt

sort $app.gt > gt_sorted

num_gt=`cat $app.gt | wc -l`
found_by_fs=`cat $app.fs | wc -l`
found_in_unsound=`cat gt_in_unsound | wc -l`

check=`comm -23 gt_in_unsound gt_sorted | wc -l`
echo "Checking:  num found in unsound run that are not there in oracle run:" $check

echo "num gt:" $num_gt
echo "found by FS:" $found_by_fs
echo "found in unsound:" $found_in_unsound

missed_by_unsound=$((num_gt - found_in_unsound))
missed_by_fs=$((num_gt - found_by_fs))

comm -23 gt_sorted gt_in_unsound > in_gt_not_in_unsound
comm -23 in_gt_not_in_unsound $app.fs > not_in_both

new_bugs=`cat not_in_both | wc -l`

rm -f gt_sorted in_gt_not_in_unsound not_in_both gt_in_unsound

alarms_unsound=`cat chord_output_mln-datarace-oracle-unsound-thresc/oracle_queries.txt | wc -l`
echo "Total Alarms unsound:" $alarms_unsound
echo "Missed by Chord:" $missed_by_unsound
echo "Missed by FS:" $missed_by_fs
echo "New bugs (missed by both):" $new_bugs

rm -f $app.fs
