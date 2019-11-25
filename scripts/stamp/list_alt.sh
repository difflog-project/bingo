#!/usr/bin/env bash

# Intended to be run from chord-fork folder

# cd ./Error-Ranking/chord-fork
# ./scripts/list_alt.sh PROGRAM PROGRAM_PATH suffix
# PROGRAM - a convenient name that represents the program being analyzed
# PROGRAM_PATH - is a path (relative to current dir) of the .apk file (including .apk filename) that represents the program
# suffix - a string that is suffixed to the name of the output folder.
# Example invocation:
# ./scripts/list_alt.sh VideoActivity stamp-benches/DarpaApps/2A_VideoGame/VideoActivity.apk kobj1


export PROGRAM=$1
export PROGRAM_PATH=`readlink -f $2`
export SUFFIX=$3

export BASE_DIR=`pwd`
export PRJ_DIR=$BASE_DIR/android_bench/stamp_output/$PROGRAM

source scripts/setpaths.sh 

PATH_SAVE=$PATH
JAVA_HOME_SAVE=$JAVA_HOME
export PATH=$BASE_DIR/../jdk/jdk1.7.0_80/bin/:$PATH
export JAVA_HOME=$BASE_DIR/../jdk/jdk1.7.0_80

DIR_SUFFIX=`basename $2 .apk`
cd stamp
mv local.config local.config.save
mkdir $PRJ_DIR 

rm -rf stamp_output/*
cp local.config.mln_problem local.config
./stamp analyze $PROGRAM_PATH 
mv stamp_output/*${DIR_SUFFIX}*/chord_output $PRJ_DIR/chord_output_mln-taint-problem_$SUFFIX
mv stamp_output/*${DIR_SUFFIX}*/log.txt $PRJ_DIR/chord_output_mln-taint-problem_$SUFFIX
mv stamp_output/*${DIR_SUFFIX}*/results $PRJ_DIR/chord_output_mln-taint-problem_$SUFFIX
mkdir $PRJ_DIR/chord_output_mln-taint-problem_$SUFFIX/store
mv stamp_output/*${DIR_SUFFIX}*/* $PRJ_DIR/chord_output_mln-taint-problem_$SUFFIX/store

mv local.config.save local.config
cd -

export PATH=$PATH_SAVE
export JAVA_HOME=$JAVA_HOME_SAVE
