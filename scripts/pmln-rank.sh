#!/usr/bin/env bash

# Intended to be run from the chord-fork folder. Automatically starts the postgres server.
# This is a very memory hungry script. Therefore, do not run this either on Mukund's laptop, or on his desktop.

export OUTPUT_REL=$1
export PROJECT_NAME=$2
export PROJECT_PATH=$3
export BASE_QUERIES=$4
export ORACLE_QUERIES=$5
export TMP_FOLDER=$6
export START_NDX=$7
export END_NDX=$8

mkdir $TMP_FOLDER

if [[ ! "$@" =~ "nopostgres" ]]; then
    ./scripts/postgres/start.sh
fi

for i in `seq $START_NDX $END_NDX`; do
    ./scripts/mln-rank.py $OUTPUT_REL \
                          $PROJECT_NAME \
                          $PROJECT_PATH \
                          $BASE_QUERIES \
                          $ORACLE_QUERIES \
                          $TMP_FOLDER/feedback-$i.mln \
                          $TMP_FOLDER/results-$i.txt \
                          $TMP_FOLDER/stats-$i.txt \
                          $TMP_FOLDER/combined-$i &
done

wait

if [[ ! "$@" =~ "nopostgres" ]]; then
    ./scripts/postgres/stop.sh
fi
