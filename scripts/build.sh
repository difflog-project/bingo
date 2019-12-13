#!/usr/bin/env bash
# set -x

# Intended to be run from chord-fork folder
# cd ./Error-Ranking/chord-fork
# ./scripts/build.sh

source ./scripts/setpaths.sh

# { prune-cons
pushd scripts/bnet/prune-cons
./build.sh
if [ $? -ne 0 ]; then
  echo "Build failed: prune-cons"
  exit 1
fi
popd
# }

# { LibDAI
git clone https://bitbucket.org/rmukundroot/libdai.git
pushd libdai
./build.sh
if [ $? -ne 0 ]; then
  echo "Build failed: LibDAI"
  exit 1
fi
popd
# }
