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
   if [ $anal == "datarace" ]; then
      query_tuple="racePairs_cs"
   else
      query_tuple="lflow"
   fi

   if [ ! -d $HOME/artifact/results/$anal/$bmk/output ]; then
      mkdir $HOME/artifact/results/$anal/$bmk/output
   fi

   cd $CFORK
   source ./scripts/setpaths.sh

   base_r_out=$HOME/artifact/results/$anal/$bmk/output/baseR
   if [ ! -d $base_r_out ]; then
      mkdir $base_r_out
      echo "Starting Base-R runs..."
      for i in `seq 1 $num_base_r_trials`
      do
         scripts/random-rank.py ${base_q[$bmk]} ${oracle_q[$bmk]} $base_r_out/combined-$i $base_r_out/stats-$i.txt > /dev/null 2>&1
      done
      echo "Done."
   else echo "Base-R data is present. Not re-running. Please delete $base_r_out to re-run."
   fi

   base_c_out=$HOME/artifact/results/$anal/$bmk/output/baseC
   if [ ! -d $base_c_out ]; then
      mkdir $base_c_out

      echo "Starting Base-C runs..."
      if [ $anal == "datarace" ]; then
         # First, do the single run to capture nichrome logs
         out_dir=$base_c_out/baseC_single
         mkdir $out_dir
         ./scripts/mln-rank-iter.py $query_tuple $bmk ${bpath[$bmk]} ${bpath[$bmk]}/chord_output_mln-datarace-problem/base_queries.txt ${bpath[$bmk]}/chord_output_mln-datarace-oracle/oracle_queries.txt $out_dir/f.txt $out_dir/r.txt $out_dir/s.txt $out_dir/combined > $out_dir/o.txt 2>&1
         mv log.txt $out_dir   
      fi

      scripts/pmln-rank.sh $query_tuple $bmk ${bpath[$bmk]} ${base_q[$bmk]} ${oracle_q[$bmk]} $base_c_out 1 2 nopostgres > $base_c_out/log1 2>&1 
      scripts/pmln-rank.sh $query_tuple $bmk ${bpath[$bmk]} ${base_q[$bmk]} ${oracle_q[$bmk]} $base_c_out 3 4 nopostgres > $base_c_out/log2 2>&1 
      echo "Done."
   else echo "Base-C data is present. Not re-running. Please delete $base_c_out to re-run."
   fi
done
