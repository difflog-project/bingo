#!/usr/bin/env bash
# set -x

source scripts/setpaths.sh
export TARGET=avrora
export TARGET_DIR=$PJBENCH/dacapo/benchmarks/$TARGET
./build.sh

> $TARGET_DIR/polySite-0cfa/log.txt
> $TARGET_DIR/polySite-0cfa/polySite.out

export CHORD_MAX_HEAP=8g
export BDDBDDB_MAX_HEAP=16g

# Base queries
# time \
# java -cp $CHORD_MAIN/chord.jar \
#      -Dchord.out.dir=polySite-0cfa \
#      -Dchord.work.dir=$TARGET_DIR \
#      -Dchord.ext.java.analysis.path=$ANALYSIS_PATH \
#      -Dchord.ext.dlog.analysis.path=$CHORD_INCUBATOR/src/ \
#      -Dchord.bddbddb.max.heap=$MAX_HEAP \
#      -Dchord.check.exclude=java.,com.,sun.,sunw.,javax.,launcher. \
#      -Dchord.max.heap=$CHORD_MAX_HEAP \
#      -Dchord.bddbddb.max.heap=$BDDBDDB_MAX_HEAP \
#      -Dchord.reflect.exclude=true \
#      -Dchord.reflect.kind=dynamic \
#      -Dchord.reuse.scope=false \
#      -Dchord.verbose=2 \
#      -Dchord.run.analyses=cipa-0cfa-dlog,ctxts-java,argCopy-dlog,cspa-0cfa-dlog,polysite-dlog_XZ89_,provenance-vis \
#      -Dchord.provenance.out_r="polySite" \
#      -Dchord.ctxt.kind=ci \
#      -Dchord.kcfa.k=0 \
#      chord.project.Boot

# Oracle queries
time \
java -cp $CHORD_MAIN/chord.jar \
     -Dchord.out.dir=polySite-0cfa \
     -Dchord.work.dir=$TARGET_DIR \
     -Dchord.ext.java.analysis.path=$ANALYSIS_PATH \
     -Dchord.ext.dlog.analysis.path=$CHORD_INCUBATOR/src/ \
     -Dchord.bddbddb.max.heap=$MAX_HEAP \
     -Dchord.check.exclude=java.,com.,sun.,sunw.,javax.,launcher. \
     -Dchord.max.heap=$CHORD_MAX_HEAP \
     -Dchord.bddbddb.max.heap=$BDDBDDB_MAX_HEAP \
     -Dchord.reflect.exclude=true \
     -Dchord.reflect.kind=dynamic \
     -Dchord.reuse.scope=false \
     -Dchord.verbose=2 \
     -Dchord.run.analyses=cipa-0cfa-dlog,ctxts-java,argCopy-dlog,cspa-kobj-dlog,polysite-dlog_XZ89_,provenance-vis \
     -Dchord.provenance.out_r="polySite" \
     -Dchord.ctxt.kind=co \
     -Dchord.kobj.k=2 \
     chord.project.Boot
