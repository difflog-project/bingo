#!/usr/bin/env bash

source $(dirname "$0")/init.sh

#################################################################################
# Main Program

if [ "$#" -lt 2 ] ; then
  echo "Usage: $0 [opt|unopt] <space-separated list of benchmarks>"  >&2
  exit 1
fi

setting=$1    # opt or unopt 
if [ "$setting" != "opt" -a "$setting" != "unopt" ]; then
   echo "The first argument to $0 can only take the values \"opt\" or \"unopt\""
   exit 1
fi

benchmarks=(${@:2})

for bmk in "${benchmarks[@]}"
do
   if [ ! -n "${bpath[$bmk]+isset}" ]; then
      echo "Unknown benchmark: $bmk"
      exit 1
   fi
   if [ $setting == "opt" ]; then
      if [ -d $CFORK/${bnet_in[$bmk]}/bnet/noaugment ]; then
         echo "Bayesian network (opt) is already present in directory $CFORK/${bnet_in[$bmk]}/bnet/noaugment. Skipping build. Delete the directory to re-build."
         continue
      fi
      if [ ${compr[$bmk]} -eq 1 ]; then
         build_scr_file=./scripts/bnet/compressed/build-bnet.sh
      else
         build_scr_file=./scripts/bnet/build-bnet.sh
      fi
   elif [ $setting == "unopt" ]; then
      if [ -d $CFORK/${bnet_in[$bmk]}/bnet/noaugment_unopt ]; then
         echo "Bayesian network (unopt) is already present in directory $CFORK/${bnet_in[$bmk]}/bnet/noaugment_unopt. Skipping build. Delete the directory to re-build."
         continue
      fi
      build_scr_file=./scripts/bnet/unopt/build-bnet.sh
   fi
   cd $CFORK
   source ./scripts/setpaths.sh
   basename1=`basename ${bnet_in[$bmk]}`
   basename2=`basename ${base_q[$bmk]}`
   pathname2=`dirname ${base_q[$bmk]}`
   basename3=`basename $pathname2`
   if [ $setting == "opt" ]; then
      echo "Building Bayesian network (opt)..."
      $build_scr_file $bmk ${bpath[$bmk]} noaugment rule-prob.txt $basename1 $basename3/$basename2 
   else 
      echo "Building Bayesian network (unopt)..."
      $build_scr_file $bmk ${bpath[$bmk]} noaugment_unopt rule-prob.txt $basename1 $basename3/$basename2 
   fi
done
