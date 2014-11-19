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
import argparse

global args

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
    global args
    owidth = create_width_dictionary(olines)
    nwidth = create_width_dictionary(nlines)
    mwidth = dict(set(owidth.items()) - set(nwidth.items()))
    print("Total missing characters in newly generated WIDTH: ", len(mwidth))
    if args.show_missing_characters:
        for key in sorted(mwidth):
            print("0x%04x : %d" %(key, mwidth[key]))
    awidth = dict(set(nwidth.items()) - set(owidth.items()))
    print("Total added characters in newly generated WIDTH: ", len(awidth))
    if args.show_added_characters:
        for key in sorted(awidth):
            print("0x%04x : %d" %(key, awidth[key]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compare the contents of LC_CTYPE in two files and check for errors.')
    parser.add_argument('-o', '--old_utf8_file',
                        nargs='?',
                        required=True,
                        type=str,
                        help='The old UTF-8 file.')
    parser.add_argument('-n', '--new_utf8_file',
                        nargs='?',
                        required=True,
                        type=str,
                        help='The new UTF-8 file.')
    parser.add_argument('-a', '--show_added_characters',
                        action='store_true',
                        help='Show characters which were added in detail.')
    parser.add_argument('-m', '--show_missing_characters',
                        action='store_true',
                        help='Show characters which were removed in detail.')
    global args
    args = parser.parse_args()

    # o_ for Original UTF-8 and n_ for New UTF-8 file
    o_lines = open(args.old_utf8_file).readlines()
    n_lines = open(args.new_utf8_file).readlines()
    print("Report on CHARMAP:")
    check_charmap(o_lines, n_lines)
    print("************************************************************\n")
    print("Report on WIDTH:")
    check_width(o_lines, n_lines)
