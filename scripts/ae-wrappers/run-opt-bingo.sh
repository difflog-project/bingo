#!/usr/bin/env bash

source $(dirname "$0")/init.sh

#################################################################################
# Main Program

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
   anal=${analysis[$bmk]}
   if [ ! -d $HOME/artifact/results/$anal/$bmk/output ]; then
      mkdir $HOME/artifact/results/$anal/$bmk/output
   fi

   cd $CFORK
   source ./scripts/setpaths.sh

   build-bnet.sh opt $bmk
   exact_out=$HOME/artifact/results/$anal/$bmk/output/exact
   if [ ! -d $exact_out ]; then
      mkdir $exact_out
      echo "Starting Bingo (opt) run..."
      ./scripts/bnet/accmd ${bnet_in[$bmk]} noaugment ${base_q[$bmk]} ${oracle_q[$bmk]} ${numiter[$bmk]} $exact_out/ &
   else echo "Bingo (opt) data is present. Not re-running. Please delete $exact_out to re-run."
   fi
   wait
   echo "Done."
done
