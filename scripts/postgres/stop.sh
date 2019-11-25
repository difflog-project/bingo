#!/usr/bin/env bash

source scripts/setpaths.sh

if [[ ! `hostname` =~ "laptop.rmukund" ]]; then
  cd ../postgresql-9.6.3/bin
  ./pg_ctl -D ../data/ stop
  # rm -rf ../data
else
  sudo systemctl stop postgresql
fi
