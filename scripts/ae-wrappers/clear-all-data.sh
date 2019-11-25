#!/usr/bin/env bash

source $(dirname "$0")/init.sh

if [ "$#" -lt 1 ] ; then
  echo "Usage: $0 <space-separated list of benchmarks>"  >&2
  exit 1
fi

benchmarks=(${@:1})

for bmk in "${benchmarks[@]}"
do
   if [ ! -n "${bpath[$bmk]+isset}" ]; then
      echo "Unknown benchmark: $bmk"
      exit 1
   fi
   bnet_dir=${bnet_in[$bmk]}
   anal=${analysis[$bmk]}
   if [ "$bnet_dir" == "" ]; then
      echo "Setup has not been run. Exiting without clearing..."
      exit 1
   fi
   if [ "$anal" == "" ]; then
      echo "Setup has not been run. Exiting without clearing..."
      exit 1
   fi
   rm -rf $CFORK/$bnet_dir/bnet/*
   rm -rf $HOME/artifact/results/$anal/$bmk/output/*
   echo "Cleared data for $bmk."
done
