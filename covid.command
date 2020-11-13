#!/bin/bash

cd ~/Desktop/python/covid

rm -r ~/Desktop/python/covid/*

echo "deleted"

git clone https://github.com/CSSEGISandData/COVID-19

cd ~/Desktop/python/covid_scripts

python COVID-intro.py
