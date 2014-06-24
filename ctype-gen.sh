#!/bin/bash
# Script to generate new ctype using gen-unicode-ctype.c and
gcc -o gen-unicode-ctype.out gen-unicode-ctype.c
./gen-unicode-ctype.out $1 $3
python gen-unicode-ctype-dcp.py $2
rm -rf unicode
