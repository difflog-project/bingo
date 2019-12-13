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


# { Stamp
pushd stamp/main 
  PATH_SAVE=$PATH
  JAVA_HOME_SAVE=$JAVA_HOME
  export PATH=$ERROR_RANKING_DIR/jdk/jdk1.7.0_80/bin/:$PATH
  export JAVA_HOME=$ERROR_RANKING_DIR/jdk/jdk1.7.0_80
  ant clean
  ant
  export PATH=$PATH_SAVE
  export JAVA_HOME=$JAVA_HOME_SAVE
popd
# }


# { RoadRunner 
pushd RoadRunner 
  PATH_SAVE=$PATH
  JAVA_HOME_SAVE=$JAVA_HOME
  export PATH=$ERROR_RANKING_DIR/jdk/jdk1.7.0_80/bin/:$PATH
  export JAVA_HOME=$ERROR_RANKING_DIR/jdk/jdk1.7.0_80
  ant clean
  ant
  export PATH=$PATH_SAVE
  export JAVA_HOME=$JAVA_HOME_SAVE
popd
# }


# { Target project
if [ ! -z ${TARGET_DIR+x} ]; then
  pushd $TARGET_DIR
  ant
  if [ $? -ne 0 ]; then
    echo "Build failed: Target"
    exit 1
  fi
  popd
fi
# }
