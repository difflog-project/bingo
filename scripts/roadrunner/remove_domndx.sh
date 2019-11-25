#!/usr/bin/env bash

#removed dom indices from racePairs_cs.txt
# Sample line before removal: 15052:org/apache/commons/logging/LogFactory.java:482  15054:org/apache/commons/logging/LogFactory.java:482
# After removal: org/apache/commons/logging/LogFactory.java:482 org/apache/commons/logging/LogFactory.java:482
in_file=$1
out_file=$2
awk -F'[:| ]' '{print $2 ":" $3 " " $6 ":" $7}' $in_file > $out_file
