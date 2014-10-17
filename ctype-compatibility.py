#!/usr/bin/python3
# -*- coding: UTF-8 -i*-
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

# This script is useful for checking backward compatibility of newly
# generated LC_CTYPE file from gen-unicode-ctype.c and gen-unicode-ctype-dcp.py
# USAGE: python check-backcompatibility.py existing_ctype_file new_ctype_file
# Existing LC_CTYPE file /usr/share/i18n/locale/i18n and new generated 'unicode-ctype'

import os
import sys

class ctype:
    def __init__(self):
        self.upper, self.lower, self.alpha, self.digit, self.space, self.cntrl, self.punct, \
            self.graph, self.printc, self.xdigit, self.blank, self.combining, self.combining3  \
            = [], [], [], [], [], [], [], [], [], [], [], [], []

"""Captures Unicode values from character class and add
to ctype struct
"""
def extract_class_and_unichars(filename, struct_ctype):
    ipfile = open(filename)
    flines = ipfile.readlines()
    linecount = len(flines)
    i = 0
    for l in flines:
        w = l.split()
        if len(w) > 1:
            if l.split()[0] == "upper":
#                print("found upper %s" %i)
                process_chars(i+1, struct_ctype.upper, flines)
            if l.split()[0] == "lower":
                process_chars(i+1, struct_ctype.lower, flines)
            if l.split()[0] == "alpha":
                process_chars(i+1, struct_ctype.alpha, flines)
            if l.split()[0] == "digit":
                process_chars(i+1, struct_ctype.digit, flines)
            if l.split()[0] == "space":
                process_chars(i+1, struct_ctype.space, flines)
            if l.split()[0] == "cntrl":
                process_chars(i+1, struct_ctype.cntrl, flines)
            if l.split()[0] == "punct":
                process_chars(i+1, struct_ctype.punct, flines)
            if l.split()[0] == "graph":
                process_chars(i+1, struct_ctype.graph, flines)
            if l.split()[0] == "print":
                process_chars(i+1, struct_ctype.printc, flines)
            if l.split()[0] == "xdigit":
                process_chars(i+1, struct_ctype.xdigit, flines)
            if l.split()[0] == "blank":
                process_chars(i+1, struct_ctype.blank, flines)
            if l.split()[1] == "\"combining\";":
#                print("combining")
                process_chars(i+1, struct_ctype.combining, flines)
            if l.split()[1] == "\"combining_level3\";":
#                print("combining_level3")
                process_chars(i+1, struct_ctype.combining3, flines)

        i = i+1
#    print("alpha chars group %s" %struct_ctype.alpha)


"""Breaks each line of i18n and unicode file into Unicode blocks
Separated by ";" and extract Unicode values and add into Struct
"""
def process_chars(line_no, list_name, flines):
        for x in range(line_no, len(flines)):
#               print(x)
                if len(flines[x].split()) < 1:
                        break
                if flines[x].split()[0] == "%":
                    continue

                else:
# Break line into Unicode value range
                    l = flines[x].strip().split(";")
                    if l[len(l)-1] != "/":
                        list_lenght = len(l)+1
                    else:
                        list_lenght = len(l)
                    for i in range (0, list_lenght-1):
                         individual_word = l[i].split("..")
#                        print(individual_word)
# For blocks of characters in  "<UXXXX>..<UXXXX>"
                         if  len(individual_word ) == 1:
#                               print(individual_word[0])
                                uni_char = individual_word[0][2:len(individual_word[0])-1]
                                hex_uni_char = hex(int(uni_char,16))
                                list_name.append(hex_uni_char)
# For blocks of characters in  "<UXXXX>..<UXXXX>"
                         if  len(individual_word ) == 2:
#                               print(individual_word)
                                uni_char1 = individual_word[0][2:len(individual_word[0])-1]
                                uni_char2 = individual_word[1][2:len(individual_word[0])-1]
#                               print(int(uni_char1,16), hex(int(uni_char1,16)))
                                count = 0
                                for i in range (int(uni_char1,16), int(uni_char2,16)+1):
                                     list_name.append(hex(int(uni_char1,16)+count))
                                     count = count + 1
# For blocks of characters in  "<UXXXX>..(2)..<UXXXX>"
                         if  len(individual_word ) == 3:
#                               print(individual_word)
                                uni_char1 = individual_word[0][2:len(individual_word[0])-1]
                                uni_char2 = individual_word[2][2:len(individual_word[0])-1]
#                               print(int(uni_char1,16), hex(int(uni_char1,16)))
#                               print(int(uni_char2,16), hex(int(uni_char2,16)))
                                count = 0
                                for i in range (int(uni_char1,16), int(uni_char2,16)+1,2):
                                     list_name.append(hex(int(uni_char1,16)+count))
                                     count = count + 2
# This condition specifically added for file generated by gen-unicode-ctype.c
# it does not break char group by line
                l = flines[x].strip().split(";")
                if l[len(l)-1] != "/":
                        break

# Compared values added in stuct
def compare_list(old_list, new_list):
    for property, value in sorted(vars(old_list).items()):
        prop = eval("new_list.%s" %property)
        print("%s: %d chars in old ctype and %d chars in new ctype" %(property, len(value), len(prop)))
        report(value, prop)

# Report values to stdout
def report(old_list, new_list):
   missing_chars = list(set(old_list)-set(old_list).intersection(set(new_list)))
   print("Missing %(number)d characters of old ctype in new ctype \n  %(list)s" %{'number': len(missing_chars), 'list': sorted(missing_chars)})
   print("\n****************************************************")


# This function compares TOLOWER, TOUPPER and TOTITLE pairs of i18n and unicode file
def check_pairs(file_old, file_new):
    ipfile = open(file_old)
    flines = ipfile.readlines()
    linecount = len(flines)
    i = 0
    for l in flines:
        w = l.split()
        if len(w) > 1:
            if l.split()[0] == "toupper":
                pair_name = "toupper"
                print("Processing for TOUPPER pair group")
                process_pairs(i+1, flines, file_new, pair_name)
                print("Completed processing for TOUPPER pair group")
            if l.split()[0] == "tolower":
                pair_name = "tolower"
                print("Processing for TOLOWER pair group")
                process_pairs(i+1, flines, file_new, pair_name)
                print("Completed processing for TOLOWER pair group")
            if l.split()[1] == "\"totitle\";":
                pair_name = "totitle"
                print("Processing for TOTITLE pair group")
                process_pairs(i+1, flines, file_new, pair_name)
                print("Completed processing for TOTITLE pair group")
        i = i + 1


""" Split the i18n file line into Unicode pairs and check into
unicode files
"""
def process_pairs(line_no, flines, file_new, pair_name):
        f = open(file_new).read()
        for x in range(line_no, len(flines)):
                if len(flines[x].split()) < 1:
                        break
                if flines[x].split()[0] == "%":
                    continue
                else:
# Break line into pairs, separated by ;
                    l = flines[x].strip().split(";")
                    if l[len(l)-1] != "/":
                        list_lenght = len(l)+1
                    else:
                        list_lenght = len(l)
                    for i in range (0, list_lenght-1):
                        if l[i] not in f:
                           print("%s not present in %s pair new ctype" %(l[i], pair_name))
# Groups are not separated by line in unicode file
                l = flines[x].strip().split(";")
                if l[len(l)-1] != "/":
                        break


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("USAGE: python check_backcompatibility existing_ctype_file new_ctype_file")
    else:
        file_i18n = sys.argv[1]
        file_unicode = sys.argv[2]
        ext_ctype = ctype()
        new_ctype = ctype()
        extract_class_and_unichars(file_i18n, ext_ctype)
        extract_class_and_unichars(file_unicode, new_ctype)
        compare_list(ext_ctype, new_ctype)
        check_pairs(file_i18n, file_unicode)
