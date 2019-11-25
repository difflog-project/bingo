#!/usr/bin/env bash

run_id=$1
sleep 10
port=`grep SRKDBG rr_runs/rr_out_$run_id | awk '{print $5;}'`
echo "Running client with port $port"
java -jar /home/sulekha/Error-Ranking/chord-fork/pjbench/ftp/lib/client.jar $port > rr_runs/cl_out_${run_id}_1 2>&1 &
java -jar /home/sulekha/Error-Ranking/chord-fork/pjbench/ftp/lib/client.jar $port > rr_runs/cl_out_${run_id}_2 2>&1 &
java -jar /home/sulekha/Error-Ranking/chord-fork/pjbench/ftp/lib/client.jar $port > rr_runs/cl_out_${run_id}_3 2>&1 &
wait
touch stop
