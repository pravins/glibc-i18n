#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

# This script generates alpha, upper and lower ctype from
# DerivedCoreProperties.txt file of UCD and add it to "unicode" file generated
# by gen-unicode-ctype.c
# USAGE: python gen_unicode_ctype_dcp.py DerivedCoreProperties.txt

import os
import sys

def process_dcp(dcp_file, outfile):
    ipfile = open(dcp_file)
    flines = ipfile.readlines()
    linecount = len(flines)
    i = 0
    for l in flines:
        w = l.split()
        if len(w) > 3:
            if (l.split()[3] == "Uppercase") and (l.split()[2] == "Property:"):
#               print("uppercase @ ", i)
               outfile.write("upper /\n")
               write_class(i+3, outfile, flines)

            if (l.split()[3] == "Lowercase") and (l.split()[2] == "Property:"):
#               print("lowercase @ ", i)
               outfile.write("lower /\n")
               write_class(i+3, outfile, flines)

            if (l.split()[3] == "Alphabetic") and (l.split()[2] == "Property:"):
#               print("alphabetic @ ", i)
               outfile.write("alpha /\n")
               write_class(i+3, outfile, flines)
        i = i+1
    ipfile.close()

def write_class(line_no, outfile, flines):
    nline_count = 0
    outfile.write("    ")
    for x in range(line_no, len(flines)):
# next time counter to write "\n" to file
        if nline_count > 6:
            outfile.write("/\n    ")
            nline_count = 0
        if len(flines[x].split()) < 1:
            continue
        if flines[x].split()[1] == "Total":
#         print(x)
            break
        if len(flines[x].split()[0].split(".."))==1:
#            print(flines[x].split()[0].split(".."))
            outfile.write( "<U"  + flines[x].split()[0].split("..")[0] + ">;")
            nline_count = nline_count + 1
        else:
#         print(flines[x].split()[0].split(".."))
            outfile.write( "<U"  + flines[x].split()[0].split("..")[0] + ">..<U" + flines[x].split()[0].split("..")[1] + ">;")
            if len(flines[x].split()[0].split("..")[0]) > 4:
                nline_count = nline_count + 3
            else:
                nline_count = nline_count + 2
    outfile.write("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: python gen_unicode_ctype_dcp.py DerivedCoreProperties.txt\n")
    else:
        dcp_file = sys.argv[1]
        outfile = open("unicode-ctype","w")
        unicode_file = open("unicode")
        flines = unicode_file.readlines()
        i = 0
        for l in flines:
                outfile.write(l)
                i = i+1
                if l == "LC_CTYPE\n":
                   break
        process_dcp(dcp_file, outfile)
        for x in range(i,len(flines)):
                outfile.write(flines[x])
        outfile.close()
        unicode_file.close()
