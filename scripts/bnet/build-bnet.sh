#!/usr/bin/env bash

# Given a project path, runs the commands that must be run before driver.py can be invoked. This includes pruning the
# constraints in named_cons_all.txt, turning named_cons_all.txt.pruned into a Bayesian network, and finally turning
# named-bnet.out into factor-graph.fg which is readable by driver.py.

# Arguments:
# 1. Project path, in a format recognized by list.sh, and eventually by runner.pl.
# 2. Augment dir: "augment" or "noaugment", suffixed with any string, in which the BN will be built.
#                 This will also indicate to prune-cons whether or not to augment the forward constraints while pruning.
#                 The second part of the name is merely a convention: it indicates the list of queries used as
#                 base_queries.txt while performing prune-cons.
#                 Ex: noaugment_or_thr means that prune-cons will not augment (because of the noaugment prefix) 
#                     and the BN will be placed in the directory noaugment_or_thr. The or_thr suffix indicates, again by
#                     convention, that the k-obj=3-sensitive oracle with thread escape was used as the set of queries to
#                     to be ranked.
# 3. rule-prob.txt, file mapping rule names to probabilities.

# Intended to be run from the main Bingo directory.
# ./scripts/bnet/build-bnet.sh pjbench/ftp noaugment_base rule-prob.txt

set -e

export PROGRAM_PATH=`readlink -f $1`
export AUGMENT_DIR=$2
export RULE_PROB_FILENAME=$3
export OP_TUPLE_FILENAME="$PROGRAM_PATH/observable-tuples.txt"

if [ ! -f $RULE_PROB_FILENAME ]; then
    >&2 echo "$RULE_PROB_FILENAME not found!"
    exit 1
fi

if [ ! -f $OP_TUPLE_FILENAME ]; then
    >&2 echo "$OP_TUPLE_FILENAME not found!"
    exit 1
fi

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

mkdir -p $PROGRAM_PATH/bnet/$AUGMENT_DIR

# Step 1: Reify EDB tuples in named_cons_all.txt
# named_cons_all.txt ==> named_cons_all.txt.edbderived
./scripts/bnet/compressed/derive-edb.py < $PROGRAM_PATH/named_cons_all.txt \
                                        > $PROGRAM_PATH/bnet/$AUGMENT_DIR/named_cons_all.txt.edbderived \
                                        2> $PROGRAM_PATH/bnet/$AUGMENT_DIR/derive-edb.log

# Step 2: Introduce proxy observation tuples to give feedback with partial confidence
./scripts/bnet/derive-observations.py $PROGRAM_PATH/bnet/$AUGMENT_DIR/named_cons_all.txt.edbderived \
                                      $PROGRAM_PATH/observed-queries.txt \
                                      $RULE_PROB_FILENAME \
                                      $PROGRAM_PATH/bnet/$AUGMENT_DIR/named_cons_all.txt.edbobsderived \
                                      $PROGRAM_PATH/bnet/$AUGMENT_DIR/$RULE_PROB_FILENAME.obs-derived

# Step 3: Remove cycles from named_cons_all.txt + various optimizations
# named_cons_all.txt ==> named_cons_all.txt.pruned
./scripts/bnet/prune-cons/prune-cons $AUGMENT $OP_TUPLE_FILENAME \
     < $PROGRAM_PATH/bnet/$AUGMENT_DIR/named_cons_all.txt.edbobsderived \
     > $PROGRAM_PATH/bnet/$AUGMENT_DIR/named_cons_all.txt.pruned.edbdobserived \
     2> $PROGRAM_PATH/bnet/$AUGMENT_DIR/prune-cons.log

# Step 4: Convert named_cons_all.txt.pruned to Bayesian network
# named_cons_all.txt.edbderived.pruned ==> (named-bnet.out, bnet-dict.out)
./scripts/bnet/cons_all2bnet.py $PROGRAM_PATH/bnet/$AUGMENT_DIR/bnet-dict.out narrowor \
    < $PROGRAM_PATH/bnet/$AUGMENT_DIR/named_cons_all.txt.pruned.edbobsderived \
    > $PROGRAM_PATH/bnet/$AUGMENT_DIR/named-bnet.out \
    2> $PROGRAM_PATH/bnet/$AUGMENT_DIR/cons_all2bnet.log

# Step 5: Wrapper.cpp works with "factor graph", not with Bayesian networks
# So, convert Bayesian network to "factor graph"
# named-bnet.out ==> factor-graph.fg
./scripts/bnet/bnet2fg.py $PROGRAM_PATH/bnet/$AUGMENT_DIR/$RULE_PROB_FILENAME.obs-derived 0.9 \
    < $PROGRAM_PATH/bnet/$AUGMENT_DIR/named-bnet.out \
    > $PROGRAM_PATH/bnet/$AUGMENT_DIR/factor-graph.fg \
    2> $PROGRAM_PATH/bnet/$AUGMENT_DIR/bnet2fg.log
