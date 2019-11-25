#!/usr/bin/env bash

if [[ ! -d scratch ]]; then
  mkdir scratch
  cd scratch
  unzip -q ../dat/luindex.zip
  cd -
fi

./compile.sh
