#!/usr/bin/env bash

grep CLASS chord_output_bytecode-count-total/log.txt > reachable_classes_total.txt
sed -i 's/CLASS: //g' reachable_classes_total.txt
./bc_loc.sh reachable_classes_total.txt > bc_loc_total_out
total_loc=`tail -n 1 bc_loc_total_out`
total_cl=`cat reachable_classes_total.txt | wc -l`
total_meth=`grep METHOD chord_output_bytecode-count-total/log.txt | wc -l`

grep CLASS chord_output_bytecode-count-app/log.txt > reachable_classes_app.txt
sed -i 's/CLASS: //g' reachable_classes_app.txt
./bc_loc.sh reachable_classes_app.txt > bc_loc_app_out
app_loc=`tail -n 1 bc_loc_app_out`
app_cl=`cat reachable_classes_app.txt | wc -l`
app_meth=`grep METHOD chord_output_bytecode-count-app/log.txt | wc -l`


echo "Total bytecode LOC:" $total_loc
echo "App bytecode LOC:" $app_loc
echo
echo "Total classes:" $total_cl
echo "App classes:" $app_cl
echo
echo "Total methods:" $total_meth
echo "App methods:" $app_meth
