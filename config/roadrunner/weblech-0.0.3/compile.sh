#! /usr/bin/env bash

ant
javac -cp classes Main.java
mv Main.class classes
