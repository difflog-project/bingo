#!/usr/bin/env bash

# Intended to be run from chord-fork folder

# cd ./Error-Ranking/chord-fork
# ./scripts/list.sh PROJECT PROJECT_PATH [noant] [oracle] [base] [thresc] [thr-or] [thr-pr] [unsound-e-or] [unsound-e-pr] [unsound-ne-or] [unsound-ne-pr]

# For example:
# ./scripts/list.sh ftp pjbench/ftp oracle base thresc thr-or thr-pr unsound-e-or unsound-e-pr unsound-ne-or unsound-ne-pr

source scripts/setpaths.sh

export PROGRAM=$1
export PROGRAM_PATH=`readlink -f $2`
export NUM_WORKERS=4

# Different settings of the following options produce different number of alarms.
# TTF is the least sound (minimum alarms) and FFT is the most sound (maximum alarms)
# -D chord.datarace.exclude.init
# -D chord.datarace.exclude.eqth
# -D chord.datarace.exclude.nongrded

if [[ ! "$@" =~ "noant" ]]; then
  pushd $PROGRAM_PATH
    mkdir -p classes
    ant
  popd
fi

##############################################################################################

if [[ "$@" =~ "oracle" ]]; then
  echo "Starting oracle with sound flag settings (FFT) at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -analysis=mln-datarace-oracle \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-oracle/oracle_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "base" ]]; then
  if [[ ! -d $PROGRAM_PATH/chord_output_mln-datarace-oracle ]]; then
      echo 'Please run the datarace oracle analysis (list.sh with the "oracle" option) before running this.' 
      exit 1
  fi
  echo "Starting base with sound flag settings (FFT) at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -analysis=mln-datarace-problem \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-problem/base_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "thresc" ]]; then
  if [[ ! -d $PROGRAM_PATH/chord_output_mln-datarace-oracle ]]; then
      echo 'Please run the datarace oracle analysis (list.sh with the "oracle" option) before running this.' 
      exit 1
  fi
  echo "Starting thread escape metaback analysis at `date`"
  time \
  ./chord_incubator/runner.pl -mode=parallel -workers=$NUM_WORKERS \
                              -analysis=thresc_metaback \
                              -program=$PROGRAM
  echo 'NOTE: This option runs chord in the master/slave mode in background.'
fi

##############################################################################################

if [[ "$@" =~ "thr-or" ]]; then
  if [[ ! -f $PROGRAM_PATH/proven_queries_mapped.txt ]]; then
      echo 'Please copy proven_queries_mapped.txt from blessed data before running this.' 
      exit 1
  fi
  echo "Starting oracle with sound flag settings (FFT) that uses thread escape data at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -D chord.reuse.scope=true \
                              -D chord.reflect.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/reflect.txt \
                              -D chord.methods.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/methods.txt \
                              -analysis=mln-datarace-oracle \
                              -D chord.mln.useThrEsc=true \
                              -D chord.mln.threscFile=$PROGRAM_PATH/proven_queries_mapped.txt \
                              -D chord.out.dir=$PROGRAM_PATH/chord_output_mln-datarace-oracle-thresc \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "thr-pr" ]]; then
  if [[ ! -f $PROGRAM_PATH/proven_queries_mapped.txt ]]; then
      echo 'Please copy proven_queries_mapped.txt from blessed data before running this.' 
      exit 1
  fi
  echo "Starting base with sound flag settings (FFT) that uses thread escape data at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -D chord.reuse.scope=true \
                              -D chord.reflect.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/reflect.txt \
                              -D chord.methods.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/methods.txt \
                              -analysis=mln-datarace-problem \
                              -D chord.mln.useThrEsc=true \
                              -D chord.mln.threscFile=$PROGRAM_PATH/proven_queries_mapped.txt \
                              -D chord.out.dir=$PROGRAM_PATH/chord_output_mln-datarace-problem-thresc \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-problem-thresc/base_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "unsound-e-or" ]]; then
  if [[ ! -f $PROGRAM_PATH/proven_queries_mapped.txt ]]; then
      echo 'Please copy proven_queries_mapped.txt from blessed data before running this.' 
      exit 1
  fi
  echo "Starting oracle with unsound flag settings (TTF) that uses thread escape data at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -D chord.reuse.scope=true \
                              -D chord.reflect.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/reflect.txt \
                              -D chord.methods.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/methods.txt \
                              -analysis=mln-datarace-oracle-unsound \
                              -D chord.mln.useThrEsc=true \
                              -D chord.mln.threscFile=$PROGRAM_PATH/proven_queries_mapped.txt \
                              -D chord.out.dir=$PROGRAM_PATH/chord_output_mln-datarace-oracle-unsound-thresc \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-oracle-unsound-thresc/oracle_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "unsound-e-pr" ]]; then
  if [[ ! -f $PROGRAM_PATH/proven_queries_mapped.txt ]]; then
      echo 'Please copy proven_queries_mapped.txt from blessed data before running this.' 
      exit 1
  fi
  echo "Starting base with unsound flag settings (TTF) that uses thread escape data at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -D chord.reuse.scope=true \
                              -D chord.reflect.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/reflect.txt \
                              -D chord.methods.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/methods.txt \
                              -analysis=mln-datarace-problem-unsound \
                              -D chord.mln.useThrEsc=true \
                              -D chord.mln.threscFile=$PROGRAM_PATH/proven_queries_mapped.txt \
                              -D chord.out.dir=$PROGRAM_PATH/chord_output_mln-datarace-problem-unsound-thresc \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-problem-unsound-thresc/base_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "unsound-ne-or" ]]; then
  if [[ ! -d $PROGRAM_PATH/chord_output_mln-datarace-oracle ]]; then
      echo 'Please run the datarace oracle analysis (list.sh with the "oracle" option) before running this.' 
      exit 1
  fi
  echo "Starting oracle with unsound flag settings (TTF) at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -D chord.reuse.scope=true \
                              -D chord.reflect.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/reflect.txt \
                              -D chord.methods.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/methods.txt \
                              -analysis=mln-datarace-oracle-unsound \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-oracle/oracle_queries.txt
fi

##############################################################################################

if [[ "$@" =~ "unsound-ne-pr" ]]; then
  if [[ ! -d $PROGRAM_PATH/chord_output_mln-datarace-oracle ]]; then
      echo 'Please run the datarace oracle analysis (list.sh with the "oracle" option) before running this.' 
      exit 1
  fi
  echo "Starting base with unsound flag settings (TTF) at `date`"
  time \
  ./chord_incubator/runner.pl -mode=serial -foreground \
                              -D chord.reuse.scope=true \
                              -D chord.reflect.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/reflect.txt \
                              -D chord.methods.file=$PROGRAM_PATH/chord_output_mln-datarace-oracle/methods.txt \
                              -analysis=mln-datarace-problem-unsound \
                              -program=$PROGRAM

  wc -l $PROGRAM_PATH/chord_output_mln-datarace-problem/base_queries.txt
fi

##############################################################################################

if [[ ! "$@" =~ "nopopups" ]]; then
  if [ -x "$(command -v zenity)" ]; then
    zenity --info --text="Finished running list.sh!" &> /dev/null &
  else
    xmessage --text="Finished running list.sh!" &> /dev/null &
  fi
fi
