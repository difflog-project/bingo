#! /usr/bin/env bash

if [[ ! -d classes ]]; then
    mkdir classes
fi
ant
javac -cp classes Main.java
mv Main.class classes
