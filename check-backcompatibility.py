#!/usr/bin/python
# -*- coding: UTF-8 -i*-
# Copyright (C) 2013-14, Pravin Satpute <psatpute@redhat.com>

#Input file for this is /usr/share/i18n/locale/i18n, It parses file and
#gather Unicode characters under different Lc_CTYPE

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os, sys

def extract_class_and_unichars(filename):
    upper = []
    lower = []
    alpha = []
    digit = []
    space = []
    cntrl = []
    punct = []
    graph = []
    printc = []
    xdigit = []
    ipfile = open(filename)
    flines = ipfile.readlines()
    linecount = len(flines)
    i = 0
    for l in flines:
	w = l.split()
	if len(w) > 1:
	    if l.split()[0] == "upper":
#                print "found uppper", i
		process_chars(i+1, upper, flines)
	    if l.split()[0] == "lower":
#                print "found uppper", i
		process_chars(i+1, lower, flines)
	    if l.split()[0] == "alpha":
#                print "found uppper", i
		process_chars(i+1, alpha, flines)
	    if l.split()[0] == "digit":
#                print "found uppper", i
		process_chars(i+1, digit, flines)
	    if l.split()[0] == "space":
#                print "found uppper", i
		process_chars(i+1, space, flines)
	    if l.split()[0] == "cntrl":
#                print "found uppper", i
		process_chars(i+1, cntrl, flines)
	    if l.split()[0] == "punct":
#                print "found uppper", i
		process_chars(i+1, punct, flines)
	    if l.split()[0] == "graph":
#                print "found uppper", i
		process_chars(i+1, graph, flines)
	    if l.split()[0] == "print":
#                print "found uppper", i
		process_chars(i+1, printc, flines)
	    if l.split()[0] == "xdigit":
#                print "found uppper", i
		process_chars(i+1, xdigit, flines)

        i = i+1
    print "xdigit chars group", xdigit

def process_chars(line_no, list_name, flines):
	for x in range(line_no, len(flines)):
#		print x
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
#			 print  individual_word
# For blocks of characters in  "<UXXXX>..<UXXXX>"
			 if  len(individual_word ) == 1:
#				print individual_word[0]
				uni_char = individual_word[0][2:len(individual_word[0])-1]
                                hex_uni_char = hex(int(uni_char,16))
				list_name.append(hex_uni_char)
# For blocks of characters in  "<UXXXX>..<UXXXX>"
			 if  len(individual_word ) == 2:
#				print individual_word
				uni_char1 = individual_word[0][2:len(individual_word[0])-1]
				uni_char2 = individual_word[1][2:len(individual_word[0])-1]
#				print int(uni_char1,16), hex(int(uni_char1,16))
				count = 0
				for i in range (int(uni_char1,16), int(uni_char2,16)+1):
                                     list_name.append(hex(int(uni_char1,16)+count))
				     count = count + 1
# For blocks of characters in  "<UXXXX>..(2)..<UXXXX>"
			 if  len(individual_word ) == 3:
#				print individual_word
				uni_char1 = individual_word[0][2:len(individual_word[0])-1]
				uni_char2 = individual_word[2][2:len(individual_word[0])-1]
#				print int(uni_char1,16), hex(int(uni_char1,16))
#				print int(uni_char2,16), hex(int(uni_char2,16))
				count = 0
				for i in range (int(uni_char1,16), int(uni_char2,16)+1,2):
                                     list_name.append(hex(int(uni_char1,16)+count))
				     count = count + 2



if __name__ == "__main__":
    existing_lc_ctype = sys.argv[1]
    extract_class_and_unichars(existing_lc_ctype)
