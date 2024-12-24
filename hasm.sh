#!/bin/bash

if [ "$1" == "test" ]; then
    python3 test/test.py
else
    python3 compiler.py "$1"
fi
