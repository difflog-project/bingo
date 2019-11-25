#! /usr/bin/env bash

ant
javac -cp classes:../../shared/dacapo-9.12/classes Main.java
mv Main.class classes
javac -cp classes:../../shared/dacapo-9.12/classes MainRR.java
mv MainRR.class classes
