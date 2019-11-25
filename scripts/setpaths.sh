#!/usr/bin/env bash

# Intended to be run from chord-fork folder
# cd ./Error-Ranking/chord-fork
# source scripts/setpaths.sh [java7]

export BASE_DIR=`pwd`
export ERROR_RANKING_DIR=$BASE_DIR/..

export CHORD_DIR=$BASE_DIR/jchord
export CHORD_MAIN=$CHORD_DIR/main
export CHORD_INCUBATOR=$BASE_DIR/chord_incubator
export STAMP=$BASE_DIR/stamp
export MLN=$BASE_DIR/mlninference
export MLN_BENCH=$BASE_DIR/mln_bench
export NICHROME=$BASE_DIR/nichrome/nichrome

export PJBENCH=$BASE_DIR/pjbench
export PAG_BENCH=$PJBENCH

export ANALYSIS_PATH=$ANALYSIS_PATH:$CHORD_INCUBATOR/classes
export ANALYSIS_PATH=$ANALYSIS_PATH:$CHORD_INCUBATOR/lib/guava-17.0.jar
export ANALYSIS_PATH=$ANALYSIS_PATH:$CHORD_INCUBATOR/lib/gurobi.jar

export PATH=$ERROR_RANKING_DIR/jdk/apache-ant-1.9.9/bin:$PATH
export ANT_HOME=$ERROR_RANKING_DIR/jdk/apache-ant-1.9.9

if [[ ! "$@" =~ "java7" ]]; then
  export PATH=$ERROR_RANKING_DIR/jdk/jdk1.6.0_45/bin/:$PATH
  export JAVA_HOME=$ERROR_RANKING_DIR/jdk/jdk1.6.0_45
else
  export PATH=$ERROR_RANKING_DIR/jdk/jdk1.7.0_80/bin/:$PATH
  export JAVA_HOME=$ERROR_RANKING_DIR/jdk/jdk1.7.0_80
fi

if [[ $HOSTNAME =~ "fir" ]]; then
   export PATH=$ERROR_RANKING_DIR/python3/Python-3.6.1/:$ERROR_RANKING_DIR/python3/pypy3-v5.8.0-linux64/bin:$PATH
else
   export PATH=$ERROR_RANKING_DIR/python3/Python-3.6.1/:$PATH
fi
export PYTHONPATH=$ERROR_RANKING_DIR/python3
