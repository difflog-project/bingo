#!/usr/bin/env bash

for i in *.html 
do
   sed 's/href=\"java\/lang\/[^"]*\"//g' $i > temp
   mv temp $i
done
