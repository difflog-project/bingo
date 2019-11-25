#!/usr/bin/env bash

source $(dirname "$0")/init.sh

if [ "$#" -lt 1 ] ; then
  echo "Usage: $0 <space-separated list of benchmarks>"  >&2
  exit 1
fi

benchmarks=(${@:1})
username=`whoami`

for bmk in "${benchmarks[@]}"
do
   if [ ! -n "${bpath[$bmk]+isset}" ]; then
      echo "Unknown benchmark: $bmk"
      exit 1
   fi
   ps -aef | grep $username | grep $bmk | grep -E "scripts.pmln-rank|scripts.mln-rank|scripts.list-nichrome|nichrome.jar" > kill_p1
   awk '{print $2;}' kill_p1 > kill_p2
   for proc_id in `cat kill_p2`
   do
      kill -9 $proc_id > /dev/null 2>&1
   done
done

# repeating again some new processed might have been spawned...
for bmk in "${benchmarks[@]}"
do
   ps -aef | grep $username | grep $bmk | grep -E "scripts.pmln-rank|scripts.mln-rank|scripts.list-nichrome|nichrome.jar" > kill_p1
   awk '{print $2;}' kill_p1 > kill_p2
   for proc_id in `cat kill_p2`
   do
      kill -9 $proc_id > /dev/null 2>&1
   done
done
rm -f kill_p1 kill_p2
