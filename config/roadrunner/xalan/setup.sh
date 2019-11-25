#!/usr/bin/env bash

#cp ../../../../RoadRunner/benchmarks/xalan/original.jar jar
ant clean
ant
#mkdir classes
./compile.sh

if [[ ! -d scratch ]]; then
  mkdir scratch
fi

cd scratch
if [[ ! -d xalan ]]; then
  unzip -q ../data/dat/xalan.zip
fi
cd -
