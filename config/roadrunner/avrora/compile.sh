#! /usr/bin/env bash

ant
javac -cp jar/avrora-cvs-20091224.jar Main.java
mv Main.class classes
