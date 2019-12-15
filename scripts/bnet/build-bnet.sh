#!/usr/bin/env bash

# Intended to be run from the main Bingo directory.
# Given a project name and a project path, runs the commands that must be run before driver.py can be invoked. This
# includes pruning the constraints in named_cons_all.txt, turning named_cons_all.txt.pruned into a bayesian network, and
# finally turning named-bnet.out into factor-graph.fg which is readable by driver.py.

# Arguments:
# 1. Project name, in a format recognized by list.sh, and eventually by runner.pl.
# 2. Project path, in a format recognized by list.sh, and eventually by runner.pl.
# 3. Augment dir: "augment" or "noaugment", suffixed with any string, in which the BN will be built.
#                 This will also indicate to prune-cons whether or not to augment the forward constraints while pruning.
#                 The second part of the name is merely a convention: it indicates the list of queries used as
#                 base_queries.txt while performing prune-cons.
#                 Ex: noaugment_or_thr means that prune-cons will not augment (because of the noaugment prefix) 
#                     and the BN will be placed in the directory noaugment_or_thr. The or_thr suffix indicates, again by
#                     convention, that the k-obj=3-sensitive oracle with thread escape was used as the set of queries to
#                     to be ranked.
# 4. rule-prob.txt, file mapping rule names to probabilities.
# 5. bnet dir: The chord_output folder that contains the named_cons_all.txt and in which the bnet should be built.
# 6. Name of the file containing the output tuples (ex. .../base_queries.txt) relative to the second argument above, i.e. project path. 
# 7. Optionally, "dolist", indicating whether to run list.sh. If supplied, list.sh is run to create the chord_output_*
#    directories. Otherwise, the chord_output directories from some previous run are used instead.
# 8. Optionally, "noprune", indicating whether to skip pruning named_cons_all.txt, and instead use a pre-existing
#    named_cons_all.txt.pruned file from a previous invocation of prune-cons.
# 9. Optionally, "oldbnet", indicating whether to use a pre-existing named-bnet.out from a previous invocation of
#    cons_all2bnet.py.

# cd ./Error-Ranking/chord-fork
# ./scripts/bnet/build-bnet.sh pjbench/ftp \
#                              noaugment_base rule-prob.txt \
#                              chord_output_mln-datarace-problem \
#                              chord_output_mln-datarace-problem/base_queries.txt

export PROGRAM_PATH=`readlink -f $1`
export AUGMENT_DIR=$2
export RULE_PROB_FILENAME=$3
export BNET_DIR=$4
export OP_TUPLE_FILENAME="$PROGRAM_PATH/$5"

if [[ $AUGMENT_DIR == noaugment* ]]
then
   export AUGMENT="noaugment"
elif [[ $AUGMENT_DIR == augment* ]]
then
   export AUGMENT="augment"
else
   echo "Invalid value for AUGMENT_DIR"
   exit 1
fi

mkdir -p $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR

./scripts/bnet/prune-cons/prune-cons $AUGMENT $OP_TUPLE_FILENAME \
     < $PROGRAM_PATH/${BNET_DIR}/named_cons_all.txt \
     > $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/named_cons_all.txt.pruned \
     2> $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/prune-cons.log

./scripts/bnet/cons_all2bnet.py $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/bnet-dict.out narrowor \
    < $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/named_cons_all.txt.pruned \
    > $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/named-bnet.out \
    2> $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/cons_all2bnet.log

./scripts/bnet/bnet2fg.py $RULE_PROB_FILENAME 0.999 \
    < $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/named-bnet.out \
    > $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/factor-graph.fg \
    2> $PROGRAM_PATH/${BNET_DIR}/bnet/$AUGMENT_DIR/bnet2fg.log
