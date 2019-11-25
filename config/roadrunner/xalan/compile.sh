#! /usr/bin/env bash


ant
javac -cp classes Main.java
#javac -cp jar/original.jar Main.java
mv Main.class classes
