#!/usr/bin/env bash
# set -v

# Intended to be run from main folder, ./Error-Ranking:
# # git clone https://username@bitbucket.org/rmukundroot/commands.git
# # ./commands/scripts/clone.sh [update]

function update_pjbench {
    PATH_SAVE=$PATH
    JAVA_HOME_SAVE=$JAVA_HOME
    ANT_HOME_SAVE=$ANT_HOME
  
    export PATH=$ERROR_RANKING_DIR/jdk/jdk1.6.0_45/bin:$ERROR_RANKING_DIR/jdk/apache-ant-1.9.9/bin:$PATH
    export JAVA_HOME=$ERROR_RANKING_DIR/jdk/jdk1.6.0_45
    export ANT_HOME=$ERROR_RANKING_DIR/jdk/apache-ant-1.9.9

    for i in hedc weblech-0.0.3 ftp jspider
    do
        cp ../commands/config/roadrunner/$i/* pjbench/$i
        cd pjbench/$i
        if [[ -f setup.sh ]]; then
            ./setup.sh
        fi
        cd -
    done
    for i in avrora hsqldb luindex xalan sunflow
    do
        if [[ -f pjbench/dacapo/benchmarks/$i/chord.properties.orig ]]; then
            rm -f pjbench/dacapo/benchmarks/$i/chord.properties.orig
        fi
        cp ../commands/config/roadrunner/$i/* pjbench/dacapo/benchmarks/$i
        cd pjbench/dacapo/benchmarks/$i
        if [[ -f setup.sh ]]; then
            ./setup.sh
        fi
        cd -
    done

    export ANT_HOME=$ANT_HOME_SAVE
    export JAVA_HOME=$JAVA_HOME_SAVE
    export PATH=$PATH_SAVE
    return
}

export ERROR_RANKING_DIR=`pwd`

if [ -z ${username+x} ]; then
  read -p 'Bitbucket username: ' username
fi

if [ -z ${passwd+x} ]; then
  read -s -p 'Bitbucket password: ' passwd
  echo
fi

if [[ ! "$@" =~ "update" ]]; then

  if [ ! -d "jdk" ]; then
    mkdir -p jdk
  fi

  pushd jdk
    if [ ! -d "jdk1.6.0_45" ]; then
      ln -s ../commands/resources/jdk/jdk-6u45-linux-x64.bin ./
      bash ./jdk-6u45-linux-x64.bin
    fi

    if [ ! -d "jdk1.7.0_80" ]; then
      ln -s ../commands/resources/jdk/jdk-7u80-linux-x64.tar.gz ./
      tar -xf jdk-7u80-linux-x64.tar.gz
    fi

    if [ ! -d "" ]; then
      ln -s ../commands/resources/jdk/sdk-tools-linux-3859397.zip ./
      unzip sdk-tools-linux-3859397.zip
      mv tools android-sdk-tools
    fi

    if [ ! -d "apache-ant-1.9.9" ]; then
      wget -c http://archive.apache.org/dist/ant/binaries/apache-ant-1.9.9-bin.tar.gz
      tar -xf apache-ant-1.9.9-bin.tar.gz
    fi
  popd

  mkdir -p chord-fork
  pushd chord-fork
    ln -s ../commands/scripts ./
  popd
fi

pushd chord-fork
  if [ -d "jchord" ]; then
    rm -rf jchord
  fi
  git clone https://bitbucket.org/psl-lab/jchord.git
  pushd jchord
    git checkout 67691a82e5285cc1c6b2e3f1cc4afdf7741ea6b7
    git apply $ERROR_RANKING_DIR/commands/config/jchord.patch
    pushd libsrc/joeq
      PATH_SAVE=$PATH
      JAVA_HOME_SAVE=$JAVA_HOME
      ANT_HOME_SAVE=$ANT_HOME

      export PATH=$ERROR_RANKING_DIR/jdk/jdk1.6.0_45/bin:$ERROR_RANKING_DIR/jdk/apache-ant-1.9.9/bin:$PATH
      export JAVA_HOME=$ERROR_RANKING_DIR/jdk/jdk1.6.0_45
      export ANT_HOME=$ERROR_RANKING_DIR/jdk/apache-ant-1.9.9

      ant clean
      ant jar
      mv joeq.jar ../../main/lib

      export ANT_HOME=$ANT_HOME_SAVE
      export JAVA_HOME=$JAVA_HOME_SAVE
      export PATH=$PATH_SAVE
    popd
    cp $ERROR_RANKING_DIR/commands/config/RelExcludeType.java main/src/chord/analyses/datarace
    cp $ERROR_RANKING_DIR/commands/config/RelExcludeTypeFlag.java main/src/chord/analyses/datarace
    cp $ERROR_RANKING_DIR/commands/config/AS.xsl main/src/chord/analyses/thread
    cp $ERROR_RANKING_DIR/commands/config/ASlist.dtd main/src/chord/analyses/thread
    ln -s $ERROR_RANKING_DIR/commands/resources/idea/jchord ./.idea
  popd

  if [ -d "chord_incubator" ]; then
    rm -rf chord_incubator
  fi
  git clone https://`echo $username`:`echo $passwd`@bitbucket.org/psl-lab/chord_incubator.git
  pushd chord_incubator
    git checkout 0b206e1421772bc1c9852c4c1823b247d255516f
    git apply $ERROR_RANKING_DIR/commands/config/chord_incubator.patch
    cp $ERROR_RANKING_DIR/commands/config/DataracePrintReport_cs.java src/chord/analyses/datarace/cs
    ln -s $ERROR_RANKING_DIR/commands/resources/idea/chord_incubator ./.idea
    # pushd ./src/chord/analyses/mln/datarace
    #   for f in $ERROR_RANKING_DIR/commands/config/xz89/*; do
    #     ln -s `readlink -f $f` ./
    #   done
    # popd
  popd

  if [ -d "pjbench" ]; then
    update_pjbench
  fi

  if [ -d "libdai" ]; then
    rm -rf libdai
  fi
  git clone https://bitbucket.org/rmukundroot/libdai.git
popd


if [[ ! "$@" =~ "update" ]]; then
  pushd chord-fork
    git clone https://`echo $username`:`echo $passwd`@bitbucket.org/psl-lab/mln_bench.git
    git clone https://bitbucket.org/psl-lab/pjbench.git
    update_pjbench

    git clone https://github.com/stephenfreund/RoadRunner.git
    pushd RoadRunner
      git apply ../../commands/config/roadrunner.patch
      pushd src/tools
        ln -s ../../../../commands/resources/fasttrack_with_locs.zip ./
        unzip fasttrack_with_locs.zip
      popd
    popd

    mkdir nichrome
    pushd nichrome
      git clone https://github.com/nichrome-project/nichrome.git
      pushd nichrome
        git checkout 9081caf83543b362393ff2a83c91d392e84bd981
        ln -s ../../../commands/config/Nichrome.conf ./
        ln -s ../../../commands/resources/idea/nichrome ./.idea
      popd

      git clone https://`echo $username`:`echo $passwd`@bitbucket.org/psl-lab/nichrome_incubator.git

      mkdir lbx
      pushd lbx
        ln -s ../../../commands/resources/lbx.tar.gz ./
        tar -xzf lbx.tar.gz
      popd

      mkdir mcsls
      pushd mcsls
        ln -s ../../../commands/resources/mcsls-linux-20130527.zip ./
        unzip mcsls-linux-20130527.zip
      popd

      mkdir mifumax
      pushd mifumax
        ln -s ../../../commands/resources/wmifumax-0.9.tgz ./
        tar -xzf wmifumax-0.9.tgz
      popd
    popd

    git clone https://`echo $username`:`echo $passwd`@bitbucket.org/rmukundroot/stamp.git

    git clone https://`echo $username`:`echo $passwd`@bitbucket.org/rmukundroot/stamp-benches.git
    mkdir -p android_bench/stamp_output

    mkdir libs
    pushd libs
      ln -s ../../commands/resources/boost_1_61_0.tgz ./
      tar -xf boost_1_61_0.tgz
      ln -s ../../commands/resources/gmp_6.1.0.tgz ./
      tar xzf gmp_6.1.0.tgz
    popd
  popd

  if [ ! -d "postgresql-9.6.3" ]; then
    wget -c https://ftp.postgresql.org/pub/source/v9.6.3/postgresql-9.6.3.tar.gz
    tar -xzf postgresql-9.6.3.tar.gz
  fi

  pushd postgresql-9.6.3
    export PG_DIST=`pwd`
    export PG_INSTALL=`pwd`

    ./configure --prefix=$PG_INSTALL --without-readline
    make -j 8
    make install

    pushd contrib/intarray; make; make install; popd
    pushd contrib/intagg; make; make install; popd

    pushd bin
      ./initdb -D ../data --no-locale
      ./pg_ctl -D ../data/ -l ../log start
      echo 'Creating user nichrome with password nichromepwd. Please enter this when prompted.'
      ./createuser -s -P nichrome
      ./createdb Nichromedb
      ./pg_ctl -D ../data/ stop
    popd

    # Postgres 9.6.3 does not seem to like Xin's configuration file. The following line has therefore been commented.
    # cp ../commands/config/postgresql.conf ./data
  popd


  if [ ! -d "python3" ]; then
    mkdir python3
  fi

  pushd python3
    wget -c https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz
    tar -xf Python-3.6.1.tar.xz
    pushd Python-3.6.1
      ./configure
      make -j 8
      ln -s ./python ./python3
    popd

    ln -s ../commands/resources/pypy3-v5.8.0-linux64.tgz ./
    tar xzf pypy3-v5.8.0-linux64.tgz

    wget http://bootstrap.pypa.io/get-pip.py
    # Expected version has checksum 3d45cef22b043b2b333baa63abaa99544e9c031d
    if [ -e get-pip.py ]; then
      chksum=`sha1sum get-pip.py | awk '{print $1;}'`
      if [ "$chksum" != "3d45cef22b043b2b333baa63abaa99544e9c031d" ]; then
         echo "Could not find the correct version of get-pip.py"
         exit 1
      fi
    fi
    PYTHONPATH=$(pwd) Python-3.6.1/python3 get-pip.py --target $(pwd)
    PYTHONPATH=$(pwd) Python-3.6.1/python -m pip install --target $(pwd) psutil
  popd

  pushd chord-fork
    ./scripts/build.sh
  popd

  if [ -x "$(command -v zenity)" ]; then
    zenity --info --text="Finished running clone.sh!" &> /dev/null &
  else
    xmessage --text="Finished running clone.sh!" &> /dev/null &
  fi
fi



##############################################

# While executing PYTHONPATH=$(pwd) Python-3.6.1/python3 get-pip.py --target $(pwd)
# if you get the error below:
# pip is configured with locations that require TLS/SSL, however the ssl module in Python is not available.
# then, do the following:

# sudo apt-get update
# PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin sudo apt-get install libssl-dev
# go to Python-3.6.1 folder, run ./configure and make -j 8 again.
# After this, continue with the execution of "get-pip" command above.
