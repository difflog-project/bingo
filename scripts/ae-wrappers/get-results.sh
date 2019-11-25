#!/usr/bin/env bash

source $(dirname "$0")/init.sh

#################################################################################
# Main Program

benchmarks=(${@:1})

cd $CFORK
source ./scripts/setpaths.sh

echo "Processing..."

for bmk in "${benchmarks[@]}"
do
   if [ ! -n "${bpath[$bmk]+isset}" ]; then
      echo "Unknown benchmark: $bmk"
      exit 1
   fi
   anal=${analysis[$bmk]}

   if [ ! -d $HOME/artifact/results/$anal/$bmk/output/logs ]; then
      mkdir $HOME/artifact/results/$anal/$bmk/output/logs
   fi

   edir=$HOME/artifact/results/$anal/$bmk/output/exact
   edir_unopt=$HOME/artifact/results/$anal/$bmk/output/exact_unopt
   bdir=$HOME/artifact/results/$anal/$bmk/output/baseC
   rdir=$HOME/artifact/results/$anal/$bmk/output/baseR
   odir=$HOME/artifact/results/$anal/$bmk/output
   logdir=$HOME/artifact/results/$anal/$bmk/output/logs

   ########  Compute Table 4 ##############
   total_alarms=`cat ${base_q[$bmk]} | wc -l`
   num_bugs=`cat ${oracle_q[$bmk]} | wc -l`
   ptp=`bc <<< "scale=5; (($num_bugs/$total_alarms) * 100)"`
   percentage_tp=`bc <<< "scale=2; (($ptp + 0.005) / 1)"`

   if [ -d "$edir" ]; then
      rm -rf $edir/rfr
      $CFORK/scripts/stats/reformat.sh $edir $edir/rfr
      $CFORK/scripts/stats/compute_rank_median.sh $edir/rfr auc $total_alarms $num_bugs > res 2>&1
      grep -q timeout res
      if [ $? -eq 0 ]; then
         exact_100p_rank="timeout"
         exact_90p_rank="timeout"
         exact_auc="timeout"
      else
         exact_100p_rank=`grep "Median rank 100%:" res | awk -F':' '{print $2;}'`
         exact_90p_rank=`grep "Median rank 90%:" res | awk -F':' '{print $2;}'`
         exact_auc=`grep "Median AUC:" res | awk -F':' '{print $2;}'`
      fi

      if [ -d "$bdir" ]; then
         $CFORK/scripts/stats/compute_rank_median.sh $bdir auc $total_alarms $num_bugs > res 2>&1
         grep -q timeout res
         if [ $? -eq 0 ]; then
            baseC_100p_rank="timeout"
            baseC_90p_rank="timeout"
            baseC_auc="timeout"
         else
            baseC_100p_rank=`grep "Median rank 100%:" res | awk -F':' '{print $2;}'`
            baseC_90p_rank=`grep "Median rank 90%:" res | awk -F':' '{print $2;}'`
            baseC_auc=`grep "Median AUC:" res | awk -F':' '{print $2;}'`
         fi
      else
         baseC_100p_rank="unknown"
         baseC_90p_rank="unknown"
         baseC_auc="unknown"
      fi

      if [ -d "$rdir" ]; then
         $CFORK/scripts/stats/compute_rank_median.sh $rdir auc $total_alarms $num_bugs > res 2>&1
         grep -q timeout res
         if [ $? -eq 0 ]; then
            baseR_100p_rank="timeout"
            baseR_90p_rank="timeout"
            baseR_auc="timeout"
         else
            baseR_100p_rank=`grep "Median rank 100%:" res | awk -F':' '{print $2;}'`
            baseR_90p_rank=`grep "Median rank 90%:" res | awk -F':' '{print $2;}'`
            baseR_auc=`grep "Median AUC:" res | awk -F':' '{print $2;}'`
         fi
      else
         baseR_100p_rank="unknown"
         baseR_90p_rank="unknown"
         baseR_auc="unknown"
      fi

      echo "$bmk: #Alarms                : Total: $total_alarms   Bugs: $num_bugs    %TP: $percentage_tp" > $odir/T4.txt
      echo "$bmk: Rank-100%-T            : Bingo: $exact_100p_rank   BaseC: $baseC_100p_rank  BaseR: $baseR_100p_rank" >> $odir/T4.txt
      echo "$bmk: Rank-90%-T             : Bingo: $exact_90p_rank   BaseC: $baseC_90p_rank  BaseR: $baseR_90p_rank" >> $odir/T4.txt
      echo "$bmk: Area under curve (AUC) : Bingo: $exact_auc   BaseC: $baseC_auc  BaseR: $baseR_auc" >> $odir/T4.txt
      rm -f res

   else
      exact_100p_rank="unknown"
      exact_90p_rank="unknown"
      exact_auc="unknown"
      baseC_100p_rank="unknown"
      baseC_90p_rank="unknown"
      baseC_auc="unknown"
   fi


   ########  Compute Figure 8 ##############
   if [ -d "$edir" ]; then
      ename="Bingo"
      bname="Base-C"
      false_alarms=$((total_alarms - num_bugs))
      roc_cmd="$CFORK/scripts/stats/roc.py $num_bugs $false_alarms $odir/F8.pdf $ename $edir/stats.txt "
      if [ -d "$bdir" ]; then
         for i in `seq 1 $num_base_c_trials`
         do
            roc_cmd="$roc_cmd $bname $bdir/stats-${i}.txt "
         done
      fi
      retval=`$roc_cmd > $logdir/F8.log 2>&1`
   fi

   ########  Compute Figure 7 ##############
   if [ -d "$edir" -a -d "$bdir" ]; then
      mkdir $odir/$bmk
      cp $edir/stats.txt $odir/$bmk
      cp $bdir/stats*.txt $odir/$bmk
      $CFORK/scripts/stats/plot_paper.py $bmk $total_alarms $num_base_c_trials $odir > $logdir/F7.log 2>&1
      mv $bmk.pdf $odir/F7.pdf
      rm -rf $odir/$bmk
   fi

   ########  Compute Table 7 ##############
   if [ $anal == "datarace" ]; then
      if [ -d "$edir" ]; then
         log_file_opt=${bnet_in[$bmk]}/bnet/noaugment/prune-cons.log
         tuple_str=`tail -n 3 $log_file_opt | head -n 1`
         bingo_tuple_opt=`echo "$tuple_str" | awk '{print $9;}'`
         bingo_tuple_opt_K=`bc <<< "scale=0; (($bingo_tuple_opt + 500) / 1000)"`
         tuple_str=`tail -n 2 $log_file_opt | head -n 1`
         bingo_clauses_opt=`echo "$tuple_str" | awk '{print $9;}'`
         bingo_clauses_opt_K=`bc <<< "scale=0; (($bingo_clauses_opt + 500) / 1000)"`
         bingo_itertime_opt=`$CFORK/scripts/stats/avg_itertime_bingo.sh $edir`
         echo "$bmk: Bingo, optimized   : #Tuples (K): $bingo_tuple_opt_K   #Clauses (K): $bingo_clauses_opt_K   Iter time (s): $bingo_itertime_opt" > $odir/T7.txt

         if [ -d "$edir_unopt" ]; then
            log_file_unopt=${bnet_in[$bmk]}/bnet/noaugment_unopt/prune-cons.log
            tuple_str=`tail -n 3 $log_file_unopt | head -n 1`
            bingo_tuple_unopt=`echo "$tuple_str" | awk '{print $9;}'`
            bingo_tuple_unopt_K=`bc <<< "scale=0; (($bingo_tuple_unopt + 500) / 1000)"`
            tuple_str=`tail -n 2 $log_file_unopt | head -n 1`
            bingo_clauses_unopt=`echo "$tuple_str" | awk '{print $9;}'`
            bingo_clauses_unopt_K=`bc <<< "scale=0; (($bingo_clauses_unopt + 500) / 1000)"`
            bingo_itertime_unopt=`$CFORK/scripts/stats/avg_itertime_bingo.sh $edir_unopt`
            echo "$bmk: Bingo, unoptimized : #Tuples (K): $bingo_tuple_unopt_K   #Clauses (K): $bingo_clauses_unopt_K   Iter time (s): $bingo_itertime_unopt" >> $odir/T7.txt
         fi

         if [ -d "$bdir" ]; then
            log_file_baseC=$bdir/baseC_single/log.txt
            tuple_str=`grep "Solving a MaxSAT problem" $log_file_baseC | tail -n 1`
            baseC_vars=`echo "$tuple_str" | awk '{print $6;}'`
            baseC_vars_K=`bc <<< "scale=0; (($baseC_vars + 500) / 1000)"`
            baseC_clauses=`echo "$tuple_str" | awk '{print $9;}'`
            baseC_clauses_K=`bc <<< "scale=0; (($baseC_clauses + 500) / 1000)"`
            baseC_itertime=`$CFORK/scripts/stats/avg_itertime_mln.sh $bdir`
            echo "$bmk: BaseC              : #Vars (K): $baseC_vars_K   #Clauses (K): $baseC_clauses_K   Iter time (s): $baseC_itertime" >> $odir/T7.txt
         fi
      fi
   fi

   ########  Compute Table 5 ##############
   if [ $anal == "datarace" ]; then
      cd ${bpath[$bmk]}
      res=`$CFORK/scripts/unknown_bugs.sh $bmk`
      total_alarms_unsound=`echo "$res" | grep "Total Alarms unsound:" | awk -F':' '{print $2;}'`
      num_bugs_unsound=`echo "$res" | grep "found in unsound:" | awk -F':' '{print $2;}'`
      missed_bugs_unsound=`echo "$res" | grep "Missed by Chord:" | awk -F':' '{print $2;}'`
      missed_bugs_fasttrack=`echo "$res" | grep "Missed by FS:" | awk -F':' '{print $2;}'`
      new_bugs=`echo "$res" | grep "New bugs (missed by both):" | awk -F':' '{print $2;}'`
      echo "$bmk: Chord, soundy       : Total: $total_alarms   Bugs: $num_bugs" > $odir/T5.txt
      echo "$bmk: Chord, unsound      : Total: $total_alarms_unsound Bugs: $num_bugs_unsound Missed: $missed_bugs_unsound" >> $odir/T5.txt
      echo "$bmk: Missed by FastTrack : $missed_bugs_fasttrack" >> $odir/T5.txt
      echo "$bmk: Bingo               : New Bugs: $new_bugs   LTR: $exact_100p_rank" >> $odir/T5.txt
      cd - > /dev/null 2>&1
   fi

   ########  Compute Table 6 ##############
   if [ $anal == "datarace" -a $bmk == "ftp" ]; then
      if [ -d "$odir/noisy" ]; then
         rm -f $odir/T6.txt
         if [ -d "$edir" -a -d "$bdir" ]; then
            echo "$bmk: Bingo (exact)    : Rank-100%-T: $exact_100p_rank   Rank-90%-T: $exact_90p_rank   AUC: $exact_auc" > $odir/T6.txt   
            echo "$bmk: Base-C (exact)   : Rank-100%-T: $baseC_100p_rank   Rank-90%-T: $baseC_90p_rank   AUC: $baseC_auc" >> $odir/T6.txt   
            echo >> $odir/T6.txt
         fi
      
         rm -rf $odir/noisy/percent_1/rfr
         $CFORK/scripts/stats/reformat.sh $odir/noisy/percent_1 $odir/noisy/percent_1/rfr
         $CFORK/scripts/stats/compute_rank_median_noisy.sh $odir/noisy/percent_1/rfr auc $total_alarms "$CFORK/${bpath[$bmk]}/noisy_01" $bmk  > res 2>&1
         grep -q timeout res
         if [ $? -eq 0 ]; then
            noisy_p1_100p_rank="timeout"
            noisy_p1_90p_rank="timeout"
            noisy_p1_auc="timeout"
         else
            noisy_p1_100p_rank=`grep "Median rank 100%:" res | awk -F':' '{print $2;}'`
            noisy_p1_90p_rank=`grep "Median rank 90%:" res | awk -F':' '{print $2;}'`
            noisy_p1_auc=`grep "Median AUC:" res | awk -F':' '{print $2;}'`
         fi
         echo "$bmk: Bingo (1% noise) : Rank-100%-T: $noisy_p1_100p_rank   Rank-90%-T: $noisy_p1_90p_rank   AUC: $noisy_p1_auc" >> $odir/T6.txt   
      
         rm -rf $odir/noisy/percent_5/rfr
         $CFORK/scripts/stats/reformat.sh $odir/noisy/percent_5 $odir/noisy/percent_5/rfr
         $CFORK/scripts/stats/compute_rank_median_noisy.sh $odir/noisy/percent_5/rfr auc $total_alarms "$CFORK/${bpath[$bmk]}/noisy_05" $bmk > res 2>&1
         grep -q timeout res
         if [ $? -eq 0 ]; then
            noisy_p5_100p_rank="timeout"
            noisy_p5_90p_rank="timeout"
            noisy_p5_auc="timeout"
         else
            noisy_p5_100p_rank=`grep "Median rank 100%:" res | awk -F':' '{print $2;}'`
            noisy_p5_90p_rank=`grep "Median rank 90%:" res | awk -F':' '{print $2;}'`
            noisy_p5_auc=`grep "Median AUC:" res | awk -F':' '{print $2;}'`
         fi
         echo "$bmk: Bingo (5% noise) : Rank-100%-T: $noisy_p5_100p_rank   Rank-90%-T: $noisy_p5_90p_rank   AUC: $noisy_p5_auc" >> $odir/T6.txt   
      
         rm -rf $odir/noisy/percent_10/rfr
         $CFORK/scripts/stats/reformat.sh $odir/noisy/percent_10 $odir/noisy/percent_10/rfr
         $CFORK/scripts/stats/compute_rank_median_noisy.sh $odir/noisy/percent_10/rfr auc $total_alarms "$CFORK/${bpath[$bmk]}/noisy_10" $bmk > res 2>&1
         grep -q timeout res
         if [ $? -eq 0 ]; then
            noisy_p10_100p_rank="timeout"
            noisy_p10_90p_rank="timeout"
            noisy_p10_auc="timeout"
         else
            noisy_p10_100p_rank=`grep "Median rank 100%:" res | awk -F':' '{print $2;}'`
            noisy_p10_90p_rank=`grep "Median rank 90%:" res | awk -F':' '{print $2;}'`
            noisy_p10_auc=`grep "Median AUC:" res | awk -F':' '{print $2;}'`
         fi
         echo "$bmk: Bingo (10% noise): Rank-100%-T: $noisy_p10_100p_rank   Rank-90%-T: $noisy_p10_90p_rank   AUC: $noisy_p10_auc" >> $odir/T6.txt   
         rm -f res
      fi
   fi
done
echo "Done. Please look for results in ${odir}"
