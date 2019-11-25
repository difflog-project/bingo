#! /usr/bin/env bash


# Intended to be run from chord-fork folder

# cd ./Error-Ranking/chord-fork
# ./scripts/roadrunner/run-rr.sh PROJECT PROJECT_PATH NUM_ITERS 

# For example:
# ./scripts/roadrunner/run-rr.sh ftp pjbench/ftp 10 

# RoadRunner requires java7 to run.
source scripts/setpaths.sh java7
cd RoadRunner
source ./msetup
cd -

export PROGRAM=$1
export PROGRAM_PATH=`readlink -f $2`
export NUM_ITERS=$3

cd $PROGRAM_PATH
./compile.sh
rm -rf rr_runs
mkdir rr_runs
for i in `seq 1 $NUM_ITERS`
do
    ./TEST > rr_runs/rr_out_$i 2>&1
done

for i in `seq 1 $NUM_ITERS`
do
    cat rr_runs/rr_out_$i >> rr_runs/combined_out
done
cd -

./scripts/roadrunner/extract.py < $PROGRAM_PATH/rr_runs/combined_out > $PROGRAM_PATH/${PROGRAM}_race.txt
if [[ -d $PROGRAM_PATH/chord_output_mln-datarace-problem ]]; then
    ./scripts/roadrunner/loc2tuple.py $PROGRAM_PATH/${PROGRAM}_race.txt $PROGRAM_PATH/chord_output_mln-datarace-problem/racePairs_cs.txt $PROGRAM_PATH/${PROGRAM}_race.out
else
    echo "Unable to run loc2tuple.py without the base run data (racePairs_cs.txt) in chord_output_mln-datarace-problem folder"
fi
