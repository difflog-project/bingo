#! /usr/bin/env bash

ant
javac -cp classes:../../shared/dacapo-9.12/classes:jar/sunflow-0.07.2.jar Main.java
mv Main.class classes
