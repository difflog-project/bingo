#!/usr/bin/env bash

# List of commands to invoke nichrome.

# IMPORTANT! Make sure to manually start the Postgres server before running this script. On most computers, this can be
# done by executing:
# ./scripts/postgres/start.sh
# On Mukund's laptop, do not start the Postgres server, for it is already running.
# After executing this script, one can terminate the Postgres server by running
# ./scripts/postgres/stop.sh

# Intended to be run from chord-fork folder
# cd ./Error-Ranking/chord-fork
# ./scripts/list-nichrome.sh PROGRAM PROGRAM_PATH ANALYSIS SOLVER FEEDBACK_MLN RESULT_FILENAME [nopopups]

# Arguments:
# 1. PROGRAM: Name of program being analyzed
# 2. PROGRAM_PATH: Path to program
# 3. ANALYSIS: Analysis to be run ("datarace" or "taint")
# 4. SOLVER: MAX-SAT solver used to solve constraints ("lbx" or "exact")
# 5. FEEDBACK_MLN: Path to file containing feedback tuples (In the same format as files such as
#    $PROGRAM_PATH/chord_output_mln-datarace-problem/infFeedback_0.05.mln)
# 6. RESULT_FILENAME: Filename in which to store results
# 7. nopopups: Flag to suppress popup when done

# For example:
# ./scripts/list-nichrome.sh ftp pjbench/ftp datarace lbx feedback.mln result.txt

source scripts/setpaths.sh

export PROGRAM=$1
export PROGRAM_PATH=`readlink -f $2`
export ANALYSIS=$3
export SOLVER=$4
export FEEDBACK_MLN=$5
export RESULT_FILENAME=$6

########################################################################################################################
# Instructions for running Nichrome

# New instructions [From https://fedoraproject.org/wiki/PostgreSQL]
# sudo postgresql-setup --initdb
# sudo systemctl enable postgresql
# sudo -u postgres createuser -s -P nichrome
# Password: nichromepwd
# sudo -u postgres createdb Nichromedb

# Old instructions [From Nichrome project Readme]
# rm -rf data/ log
# pg_ctl init -D data
# pg_ctl start -D data -l log
# firewall-cmd --add-port=5432/tcp
# createuser -s -P Nichrome
# createdb Nichromedb

export PROBLEM_EDB=$PROGRAM_PATH/chord_output_mln-$ANALYSIS-problem/problem.edb
if [[ $ANALYSIS == "datarace" ]]; then
  export ANALYSIS_MLN=$MLN_BENCH/program_analyses/datarace.mln
elif [[ $ANALYSIS == "taint" ]]; then
  export ANALYSIS_MLN=$STAMP/main/mln/taint.mln
else
  echo "Unknown analysis $ANALYSIS. Stopping list-nichrome.sh"
  exit 1
fi
export REV_OR_MLN=$CHORD_INCUBATOR/src/chord/analyses/mln/rev_or.mln
# export FEEDBACK_MLN=$PROGRAM_PATH/chord_output_mln-$ANALYSIS-problem/infFeedback_0.05.mln
# export FEEDBACK_MLN=feedback.mln
export REVERTED_CONS_TXT=$PROGRAM_PATH/chord_output_mln-$ANALYSIS-problem/reverted_cons_all.txt
export CONS_ALL=$PROGRAM_PATH/chord_output_mln-$ANALYSIS-problem/cons_all.txt

export GC_IN=$PROGRAM_PATH/chord_output_mln-$ANALYSIS-problem/gc_in.txt
export GC_OUT=$PROGRAM_PATH/chord_output_mln-$ANALYSIS-problem/gc_out.txt
if [ -f $GC_IN ]; then
  export GC_IN_CMD="-loadgc $GC_IN"
else
  export GC_IN_CMD=
fi

# export LBX_TIMEOUT=18000
export LBX_TIMEOUT=180

export LBX_LIMIT=1
# export LBX_LIMIT=10

# firewall-cmd --add-port=5432/tcp

echo "Starting nichrome at `date`"
time \
java -Xmx24g \
     -jar $NICHROME/main/nichrome.jar \
     MLN \
     -conf $NICHROME/Nichrome.conf \
     -e $PROBLEM_EDB \
     -r $RESULT_FILENAME \
     -i $ANALYSIS_MLN,$REV_OR_MLN,$FEEDBACK_MLN \
     -loadrev $REVERTED_CONS_TXT \
     -loadgc $CONS_ALL \
     -verbose 2 \
     -ignoreWarmGCWeight \
     -solver $SOLVER \
     -lbxTimeout $LBX_TIMEOUT \
     -lbxLimit $LBX_LIMIT \
     -printVio \
     -fullyGround \
     $GC_IN_CMD \
     -storegc $GC_OUT \
     | tee log.txt

grep -inr '^Cost' log.txt
grep -inr '^Sum' log.txt

if [[ ! "$@" =~ "nopopups" ]]; then
  if [ -x "$(command -v zenity)" ]; then
    zenity --info --text="Finished running list-nichrome.sh!" &> /dev/null &
  else
    xmessage --text="Finished running list-nichrome.sh!" &> /dev/null &
  fi
fi
