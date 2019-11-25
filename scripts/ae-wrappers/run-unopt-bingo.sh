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

   if [ $anal == "datarace" ]; then
      build-bnet.sh unopt $bmk
      exact_unopt_out=$HOME/artifact/results/$anal/$bmk/output/exact_unopt
      if [ ! -d $exact_unopt_out ]; then
         mkdir $exact_unopt_out
         echo "Starting Bingo (unopt) run..."
         ./scripts/bnet/accmd ${bnet_in[$bmk]} noaugment_unopt ${base_q[$bmk]} ${oracle_q[$bmk]} ${numiter[$bmk]} $exact_unopt_out/ &
      else echo "Bingo (unopt) data is present. Not re-running. Please delete $exact_unopt_out to re-run."
      fi
   else echo "Unoptimized Bingo runs are supported only for datarace analysis since they are very time-consuming."
   fi
   wait
   echo "Done."
done
