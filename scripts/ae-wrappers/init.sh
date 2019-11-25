#!/usr/bin/env bash

export CFORK=$HOME/artifact/Error-Ranking/chord-fork

#################################################################################
# Initialization
benchmarks=()

# Benchmark defaults

declare -A analysis 
analysis[testpgm]=datarace
analysis[hedc]=datarace
analysis[ftp]=datarace
analysis[weblech]=datarace
analysis[jspider]=datarace
analysis[avrora]=datarace
analysis[luindex]=datarace
analysis[sunflow]=datarace
analysis[xalan]=datarace

analysis["app-324"]=taint
analysis["noisy-sounds"]=taint
analysis["app-ca7"]=taint
analysis["app-kQm"]=taint
analysis["tilt-mazes"]=taint
analysis["andors-trail"]=taint
analysis["ginger-master"]=taint
analysis["app-018"]=taint


declare -A bpath
bpath[testpgm]=pjbench/testpgm
bpath[hedc]=pjbench/hedc
bpath[ftp]=pjbench/ftp
bpath[weblech]=pjbench/weblech-0.0.3
bpath[jspider]=pjbench/jspider
bpath[avrora]=pjbench/dacapo/benchmarks/avrora
bpath[luindex]=pjbench/dacapo/benchmarks/luindex
bpath[sunflow]=pjbench/dacapo/benchmarks/sunflow
bpath[xalan]=pjbench/dacapo/benchmarks/xalan

bpath["app-324"]="android_bench/stamp_output/app-324"
bpath["noisy-sounds"]="android_bench/stamp_output/noisy-sounds"
bpath["app-ca7"]="android_bench/stamp_output/app-ca7"
bpath["app-kQm"]="android_bench/stamp_output/app-kQm"
bpath["tilt-mazes"]="android_bench/stamp_output/tilt-mazes"
bpath["andors-trail"]="android_bench/stamp_output/andors-trail"
bpath["ginger-master"]="android_bench/stamp_output/ginger-master"
bpath["app-018"]="android_bench/stamp_output/app-018"

declare -A compr 
compr[testpgm]=1
compr[hedc]=1
compr[ftp]=0
compr[weblech]=1
compr[jspider]=1
compr[avrora]=1
compr[luindex]=1
compr[sunflow]=1
compr[xalan]=1

compr["app-324"]=1
compr["noisy-sounds"]=1
compr["app-ca7"]=1
compr["app-kQm"]=1
compr["tilt-mazes"]=1
compr["andors-trail"]=1
compr["ginger-master"]=1
compr["app-018"]=1

declare -A numiter 
numiter[testpgm]=500
numiter[hedc]=500
numiter[ftp]=500
numiter[weblech]=500
numiter[jspider]=500
numiter[avrora]=500
numiter[luindex]=500
numiter[sunflow]=250
numiter[xalan]=500

numiter["app-324"]=500
numiter["noisy-sounds"]=500
numiter["app-ca7"]=500
numiter["app-kQm"]=500
numiter["tilt-mazes"]=500
numiter["andors-trail"]=500
numiter["ginger-master"]=500
numiter["app-018"]=500


declare -A base_q
base_q[testpgm]=pjbench/testpgm/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[hedc]=pjbench/hedc/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[ftp]=pjbench/ftp/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[weblech]=pjbench/weblech-0.0.3/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[jspider]=pjbench/jspider/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[avrora]=pjbench/dacapo/benchmarks/avrora/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[luindex]=pjbench/dacapo/benchmarks/luindex/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[sunflow]=pjbench/dacapo/benchmarks/sunflow/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt
base_q[xalan]=pjbench/dacapo/benchmarks/xalan/chord_output_mln-datarace-oracle-thresc/oracle_queries.txt

base_q["app-324"]="android_bench/stamp_output/app-324/chord_output_mln-taint-problem/base_queries.txt"
base_q["noisy-sounds"]="android_bench/stamp_output/noisy-sounds/chord_output_mln-taint-problem/base_queries.txt"
base_q["app-ca7"]="android_bench/stamp_output/app-ca7/chord_output_mln-taint-problem/base_queries.txt"
base_q["app-kQm"]="android_bench/stamp_output/app-kQm/chord_output_mln-taint-problem/base_queries.txt"
base_q["tilt-mazes"]="android_bench/stamp_output/tilt-mazes/chord_output_mln-taint-problem/base_queries.txt"
base_q["andors-trail"]="android_bench/stamp_output/andors-trail/chord_output_mln-taint-problem/base_queries.txt"
base_q["ginger-master"]="android_bench/stamp_output/ginger-master/chord_output_mln-taint-problem/base_queries.txt"
base_q["app-018"]="android_bench/stamp_output/app-018/chord_output_mln-taint-problem/base_queries.txt"

declare -A oracle_q
oracle_q[testpgm]=pjbench/testpgm/testpgm.gt
oracle_q[hedc]=pjbench/hedc/hedc.gt
oracle_q[ftp]=pjbench/ftp/ftp.gt
oracle_q[weblech]=pjbench/weblech-0.0.3/weblech.gt
oracle_q[jspider]=pjbench/jspider/jspider.gt
oracle_q[avrora]=pjbench/dacapo/benchmarks/avrora/avrora.gt
oracle_q[luindex]=pjbench/dacapo/benchmarks/luindex/luindex.gt
oracle_q[sunflow]=pjbench/dacapo/benchmarks/sunflow/sunflow.gt
oracle_q[xalan]=pjbench/dacapo/benchmarks/xalan/xalan.gt

oracle_q["app-324"]="android_bench/stamp_output/app-324/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["noisy-sounds"]="android_bench/stamp_output/noisy-sounds/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["app-ca7"]="android_bench/stamp_output/app-ca7/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["app-kQm"]="android_bench/stamp_output/app-kQm/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["tilt-mazes"]="android_bench/stamp_output/tilt-mazes/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["andors-trail"]="android_bench/stamp_output/andors-trail/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["ginger-master"]="android_bench/stamp_output/ginger-master/chord_output_mln-taint-oracle/oracle_queries.txt"
oracle_q["app-018"]="android_bench/stamp_output/app-018/chord_output_mln-taint-oracle/oracle_queries.txt"

declare -A bnet_in
bnet_in[testpgm]=pjbench/testpgm/chord_output_mln-datarace-problem-thresc
bnet_in[hedc]=pjbench/hedc/chord_output_mln-datarace-problem-thresc
bnet_in[ftp]=pjbench/ftp/chord_output_mln-datarace-problem-thresc
bnet_in[weblech]=pjbench/weblech-0.0.3/chord_output_mln-datarace-problem-thresc
bnet_in[jspider]=pjbench/jspider/chord_output_mln-datarace-problem-thresc
bnet_in[avrora]=pjbench/dacapo/benchmarks/avrora/chord_output_mln-datarace-problem-thresc
bnet_in[luindex]=pjbench/dacapo/benchmarks/luindex/chord_output_mln-datarace-problem-thresc
bnet_in[sunflow]=pjbench/dacapo/benchmarks/sunflow/chord_output_mln-datarace-problem-thresc
bnet_in[xalan]=pjbench/dacapo/benchmarks/xalan/chord_output_mln-datarace-problem-thresc

bnet_in["app-324"]="android_bench/stamp_output/app-324/chord_output_mln-taint-problem"
bnet_in["noisy-sounds"]="android_bench/stamp_output/noisy-sounds/chord_output_mln-taint-problem"
bnet_in["app-ca7"]="android_bench/stamp_output/app-ca7/chord_output_mln-taint-problem"
bnet_in["app-kQm"]="android_bench/stamp_output/app-kQm/chord_output_mln-taint-problem"
bnet_in["tilt-mazes"]="android_bench/stamp_output/tilt-mazes/chord_output_mln-taint-problem"
bnet_in["andors-trail"]="android_bench/stamp_output/andors-trail/chord_output_mln-taint-problem"
bnet_in["ginger-master"]="android_bench/stamp_output/ginger-master/chord_output_mln-taint-problem"
bnet_in["app-018"]="android_bench/stamp_output/app-018/chord_output_mln-taint-problem"

num_base_c_trials=4
num_base_r_trials=5
num_noise_trials=3

#################################################################################
