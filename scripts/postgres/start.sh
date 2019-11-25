#!/usr/bin/env bash

source scripts/setpaths.sh

if [[ ! `hostname` =~ "laptop.rmukund" ]]; then
  cd ../postgresql-9.6.3/bin
  # ./initdb -D ../data --no-locale
  ./pg_ctl -D ../data/ -l ../log start
  # ./createuser -s -P nichrome
  # ./createdb Nichromedb
else
  sudo systemctl start postgresql
fi
sleep 5
