#! /usr/bin/env bash

PATH_SAVE=$PATH
JAVA_HOME_SAVE=$JAVA_HOME
export PATH=../../../jdk/jdk1.6.0_45/bin/:$PATH
export JAVA_HOME=../../../jdk/jdk1.6.0_45
ant
javac -cp classes Main.java
export PATH=$PATH_SAVE
export JAVA_HOME=$JAVA_HOME_SAVE
mv Main.class classes
