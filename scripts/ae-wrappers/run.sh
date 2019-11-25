#!/usr/bin/env bash

$(dirname "$0")/run-opt-bingo.sh $1
$(dirname "$0")/run-unopt-bingo.sh $1
$(dirname "$0")/run-baselines.sh $1
$(dirname "$0")/get-results.sh $1
