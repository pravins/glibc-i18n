#!/bin/bash
# Script to generate new ctype using gen-unicode-ctype.c and 
# gen-unicode-ctype-dcp.py
# Copyright (C) 2014 Free Software Foundation, Inc.
# This file is part of the GNU C Library.
# Contributed by Pravin Satpute <psatpute@redhat.com>, 2014.
#
# The GNU C Library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# The GNU C Library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with the GNU C Library; if not, see
# <http://www.gnu.org/licenses/>.

if [ $# -eq 0 ]; then
    echo "USAGE: ./ctype-gen.sh UnicodeData.txt DerivedCoreProperties.txt VERSION"
    exit 1
fi
gcc -o gen-unicode-ctype.out gen-unicode-ctype.c
./gen-unicode-ctype.out $1 $3
python gen-unicode-ctype-dcp.py $2
rm -rf unicode
