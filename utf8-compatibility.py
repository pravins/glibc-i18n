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

def check_charmap(original, new):
    ocharmap = {}
    ncharmap = {}
    i = 0
    for l in new:
        w = l.split()
        if len(w) > 0:
            if w[0] == "CHARMAP":
                create_dict(ncharmap, new, i+1)
                break
        i = i + 1

    i = 0
    for l in original:
        w = l.split()
        if len(w) > 0:
            if w[0] == "CHARMAP":
                for x in range(i+1, len(original)):
                    w = original[x].split()
                    if w[0] == "END":
                        break
                    try:
                        if ncharmap[w[0]] != w[1]:
                            print("This character might be missing in generated charmap: ", w[0])
                    except KeyError:
                        if  w[0] !='%':
                            print("This character might be missing in new generated charmap: ", w[0])
        i = i + 1

def create_dict(name, lines, i):
    for x in range(i, len(lines)):
        w = lines[x].split()
        if w[0] == "END":
            break
        name[w[0]] = w[1]

def process_chars(line_no, lines, dictionary):
    for x in range(line_no, len(lines)):
        w = lines[x].split()
        if w[0] == "END":
            break
        if w[0].find("...")==-1:
            uni_char = w[0][2:len(w[0])-1]
            hex_uni_char = hex(int(uni_char,16))
            dictionary[hex_uni_char]= w[1]
        else:
            wc = w[0].split("...")
            uni_char1 = wc[0][2:len(wc[0])-1]
            hex_uni_char1 = hex(int(uni_char1,16))
            uni_char2 = wc[1][2:len(wc[0])-1]
            hex_uni_char2 = hex(int(uni_char2,16))
            count = 0
            for i in range (int(uni_char1,16), int(uni_char2,16)+1):
                dictionary[hex(int(uni_char1,16)+count)] = w[1]
                count = count +1

def extract_univalue_and_width(lines, dictionary):
    i = 0
    for l in lines:
        w = l.split()
        if len(w) > 0:
            if w[0] == "WIDTH":
                process_chars(i+1, lines, dictionary)
                break
        i = i + 1

def check_width(olines, nlines):
    owidth = {}
    nwidth = {}
    extract_univalue_and_width(olines, owidth)
    extract_univalue_and_width(nlines, nwidth)
    mwidth = dict(set(owidth.items()) - set(owidth.items()).intersection(nwidth.items()))
    print("Total missing characters in newly generated WIDTH: ", len(mwidth))
    for key, value in sorted(mwidth.items()):
        print("{} : {}".format(key, value))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: python utf8-compatibility existing_utf8_file new_utf8_file ")
    else:
        # o_ for Original UTF-8 and n_ for New UTF-8 file
        o_utf8 = open(sys.argv[1])
        n_utf8 = open(sys.argv[2])
        o_lines = o_utf8.readlines()
        n_lines = n_utf8.readlines()
        print("Report on CHARMAP:")
        check_charmap(o_lines, n_lines)
        print("************************************************************\n")
        print("Report on WIDTH:")
        check_width(o_lines, n_lines)
