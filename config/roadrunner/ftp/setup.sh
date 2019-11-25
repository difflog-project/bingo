#!/usr/bin/env bash

mv CommandLine.java src/org/apache/ftpserver/commandline
mv CommandLineWithClient.java src/org/apache/ftpserver/commandline

if [[ ! -d classes ]]; then
  mkdir classes
fi

ant clean; ant
./compile.sh
