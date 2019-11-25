#!/usr/bin/env bash

if [[ ! -d classes/avrora/simaction ]]; then
  mkdir -p classes/avrora/actions
fi
mv SimAction.class classes/avrora/actions 

if [[ ! -d scratch ]]; then
  mkdir scratch
fi

./compile.sh

cd scratch
if [[ ! -d test ]]; then
  unzip -q ../data/dat/avrora.zip
fi
cd -
