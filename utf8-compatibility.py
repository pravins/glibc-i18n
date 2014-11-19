#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Free Software Foundation, Inc.
# This file is part of the GNU C Library.
# Contributed by Pravin Satpute <psatpute@redhat.com>, 2014.
#                Mike FABIAN <mfabian@redhat.com>, 2014
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

# This script is useful for checking backward compatibility of newly
# generated UTF-8 file from utf8-gen.py script
# USAGE: python utf8-compatibility.py existing_utf8_file new_utf8_file
import sys

def create_charmap_dictionary(lines):
    charmap_dictionary = {}
    start = False
    for l in lines:
        w = l.split()
        if len(w) > 0 and w[0] == 'CHARMAP':
            start = True
            continue
        if start == False:
            continue
        if w[0] == "END":
            return charmap_dictionary
        charmap_dictionary[w[0]] = w[1]

def check_charmap(original, new):
    ocharmap = create_charmap_dictionary(original)
    ncharmap = create_charmap_dictionary(new)
    for key in ocharmap:
        if key in ncharmap:
            if ncharmap[key] != ocharmap[key]:
                print('This character might be missing in the generated charmap: ', key)
        else:
            if key !='%':
                print('This character might be missing in the generated charmap: ', key)

def create_width_dictionary(lines):
    width_dictionary = {}
    start = False
    for l in lines:
        w = l.split()
        if len(w) > 0 and w[0] == 'WIDTH':
            start = True
            continue
        if start == False:
            continue
        if w[0] == 'END':
            return width_dictionary
        if not '...' in w[0]:
            width_dictionary[int(w[0][2:len(w[0])-1], 16)] = int(w[1])
        else:
            wc = w[0].split("...")
            for i in range(int(wc[0][2:len(wc[0])-1], 16),
                           int(wc[1][2:len(wc[0])-1], 16) + 1):
                width_dictionary[i] = int(w[1])

def check_width(olines, nlines):
    owidth = create_width_dictionary(olines)
    nwidth = create_width_dictionary(nlines)
    mwidth = dict(set(owidth.items()) - set(nwidth.items()))
    print("Total missing characters in newly generated WIDTH: ", len(mwidth))
    for key in sorted(mwidth):
        print("0x%04x : %d" %(key, mwidth[key]))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: python utf8-compatibility existing_utf8_file new_utf8_file ")
    else:
        # o_ for Original UTF-8 and n_ for New UTF-8 file
        o_lines = open(sys.argv[1]).readlines()
        n_lines = open(sys.argv[2]).readlines()
        print("Report on CHARMAP:")
        check_charmap(o_lines, n_lines)
        print("************************************************************\n")
        print("Report on WIDTH:")
        check_width(o_lines, n_lines)
