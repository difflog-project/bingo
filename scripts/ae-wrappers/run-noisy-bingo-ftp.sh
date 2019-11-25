#!/usr/bin/env bash

source $(dirname "$0")/init.sh

#################################################################################
# Main Program

if [ "$#" -gt 1 ] ; then
  echo "Usage: $0" 
  exit 1
fi


bmk=ftp 
anal=datarace

if [ ! -d $HOME/artifact/results/$anal/$bmk/output ]; then
   mkdir $HOME/artifact/results/$anal/$bmk/output
fi

cd $CFORK
source ./scripts/setpaths.sh

if [ ! -d $CFORK/${bnet_in[$bmk]}/bnet/noaugment ]; then
   build-bnet.sh opt $bmk
fi
noisy_out=$HOME/artifact/results/$anal/$bmk/output/noisy
if [ ! -d $noisy_out ]; then
   mkdir $noisy_out
   echo "Starting Bingo (1% noisy) runs for program ${bmk}..."
   mkdir $noisy_out/percent_1
   for i in `seq 1 $num_noise_trials`
   do
      ./scripts/bnet/accmd ${bnet_in[$bmk]} noaugment ${base_q[$bmk]} ${bpath[$bmk]}/noisy_01_${i}_${bmk}.gt ${numiter[$bmk]} $noisy_out/percent_1/${i}_ &
   done
   wait
   echo "Done."

   echo "Starting Bingo (5% noisy) runs for program ${bmk}..."
   mkdir $noisy_out/percent_5
   for i in `seq 1 $num_noise_trials`
   do
      ./scripts/bnet/accmd ${bnet_in[$bmk]} noaugment ${base_q[$bmk]} ${bpath[$bmk]}/noisy_05_${i}_${bmk}.gt ${numiter[$bmk]} $noisy_out/percent_5/${i}_ &
   done
   wait
   echo "Done."

   echo "Starting Bingo (10% noisy) runs for program ${bmk}..."
   mkdir $noisy_out/percent_10
   for i in `seq 1 $num_noise_trials`
   do
      ./scripts/bnet/accmd ${bnet_in[$bmk]} noaugment ${base_q[$bmk]} ${bpath[$bmk]}/noisy_10_${i}_${bmk}.gt ${numiter[$bmk]} $noisy_out/percent_10/${i}_ &
   done
   wait
   echo "Done."
else echo "Bingo (noisy) data for ftp is present. Not re-running. Please delete $noisy_out to re-run."
fi
