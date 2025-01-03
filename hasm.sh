#!/bin/bash

if [ "$1" == "test" ]; then
    python3 test/test.py
elif [ "$1" == "-o" ]; then
    python3 compiler.py "$2"
else
    echo "provide argument"
    echo "hasm -o file to compile file"
    echo "test to test all feactures"
fi