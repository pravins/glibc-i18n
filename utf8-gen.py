#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Free Software Foundation, Inc.
# This file is part of the GNU C Library.
# Contributed by
# Pravin Satpute <psatpute AT redhat DOT com> and
# Mike Fabian <mfabian At redhat DOT com> - 2014
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
# Usage: python3 utf8-gen.py UnicodeData.txt EastAsianWidth.txt
# It will output UTF-8 file
# For issues upstream https://github.com/pravins/glibc-i18n

import os,sys,re

''' Where UnicodeData.txt file has given characters in range
    Example:
    3400;<CJK Ideograph Extension A, First>;Lo;0;L;;;;;N;;;;;
    4DB5;<CJK Ideograph Extension A, Last>;Lo;0;L;;;;;N;;;;;

    UTF-8 file mention these range by adding 0x3F inbetween First and Last Unicode character.
    Example:
    <U3400>..<U343F>     /xe3/x90/x80         <CJK Ideograph Extension A>
    .
    .
    <U4D80>..<U4DB5>     /xe4/xb6/x80         <CJK Ideograph Extension A>

   NOTE:
   2000-09-24  Bruno Haible  <haible@clisp.cons.org>
   * charmaps/UTF-8: Expand <Hangul Syllable> and <Private Use> ranges,
   so they become printable and carry a width.  Comment out surrogate
   ranges.  Add a WIDTH table.
'''
def process_range(start, end, outfile, name):
    if name.find("Hangul Syllable")!=-1:
        for i in range(int(start, 16), int(end, 16)+1 ):
            unihex = chr(i).encode("UTF-8")
            hexword = convert_to_hex(unihex)
            outfile.write("<U"+('%x' % i).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")


    else:
        for i in range(int(start, 16), int(end, 16), 64 ):
            unihex = chr(i).encode("UTF-8")
            hexword = convert_to_hex(unihex)

            if i > (int(end, 16)-64):
                if len(start) == 4:
                    outfile.write("<U"+('%x' % i).upper()+">.." +  "<U"+('%x' % int(end, 16)).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")
                elif len(start) == 5:
                    outfile.write("<U000"+('%x' % i).upper()+">.." +  "<U000"+('%x' % int(end, 16)).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")
                else:
                    outfile.write("<U00"+('%x' % i).upper()+">.." +  "<U00"+('%x' % int(end, 16)).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")
                break

            if len(start) == 4:
                outfile.write("<U"+('%x' % i).upper()+">.." +  "<U"+('%x' % (i+63)).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")
            elif len(start) == 5:
                outfile.write("<U000"+('%x' % i).upper()+">.." +  "<U000"+('%x' % (i+63)).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")
            else:
                outfile.write("<U00"+('%x' % i).upper()+">.." +  "<U00"+('%x' % (i+63)).upper()+">     " + hexword + " " + name.split(",")[0] + ">" + "\n")

def process_charmap(flines, outfile):
    '''This function takes an array which contains *all* lines of
    of UnicodeData.txt and write lines to outfile as used in the

    CHARMAP
    …
    END CHARMAP

    section of the UTF-8 file in glibc/localedata/charmaps/UTF-8.

    Samples for input lines:

    0010;<control>;Cc;0;BN;;;;;N;DATA LINK ESCAPE;;;;
    3400;<CJK Ideograph Extension A, First>;Lo;0;L;;;;;N;;;;;
    4DB5;<CJK Ideograph Extension A, Last>;Lo;0;L;;;;;N;;;;;
    D800;<Non Private Use High Surrogate, First>;Cs;0;L;;;;;N;;;;;
    DB7F;<Non Private Use High Surrogate, Last>;Cs;0;L;;;;;N;;;;;
    100000;<Plane 16 Private Use, First>;Co;0;L;;;;;N;;;;;
    10FFFD;<Plane 16 Private Use, Last>;Co;0;L;;;;;N;;;;;

    Samples for output lines (Unicode-Value UTF-8-HEX Unicode-Char-Name):

    <U0010>     /x10 DATA LINK ESCAPE
    <U3400>..<U343F>     /xe3/x90/x80 <CJK Ideograph Extension A>
    %<UD800>     /xed/xa0/x80 <Non Private Use High Surrogate, First>
    %<UDB7F>     /xed/xad/xbf <Non Private Use High Surrogate, Last>
    <U0010FFC0>..<U0010FFFD>     /xf4/x8f/xbf/x80 <Plane 16 Private Use>

    '''
    l = 0
    while l < len(flines):
        w = flines[l].split(";")

        # Getting UTF8 of Unicode characters.
        # In Python3, .encode('UTF-8') does not work for
        # surrogates. Therefore, we use this conversion table
        surrogates = {
            'D800': '/xed/xa0/x80',
            'DB7F': '/xed/xad/xbf',
            'DB80': '/xed/xae/x80',
            'DBFF': '/xed/xaf/xbf',
            'DC00': '/xed/xb0/x80',
            'DFFF': '/xed/xbf/xbf',
            }
        if w[0] in surrogates:
            hexword = surrogates[w[0]]
        else:
            unihex = chr(int(w[0],16)).encode("UTF-8")
            hexword = convert_to_hex(unihex)

        ''' Some characters have <control> as a name, so using "Unicode 1.0 Name"
            Characters U+0080, U+0081, U+0084 and U+0099 has "<control>" as a name and even no "Unicode 1.0 Name" (10th field) in UnicodeData.txt
            We can write code to take there alternate name from NameAliases.txt '''
        if w[1] == "<control>":
            if w[10] != "":
                w[1] = w[10]

        # Surrogates are disabled in UTF-8 file
        if w[1].find("Surrogate,")!=-1:
            if len(w[0]) == 4:
                outfile.write("%<U"+w[0]+">     " + hexword + " " + w[1] + "\n")
            else:
                outfile.write("%<U000"+w[0]+">     " + hexword + " " + w[1] + "\n")
            l = l +1
            continue

        # Handling case of CJK IDEOGRAPH Start (3400) and End(4DB5), ADD 0x3F and create range. some more cases like this
        if w[1].find(", First>")!=-1:
            start = w[0]
            end = flines[l+1].split(";")[0]
            process_range(start, end, outfile, w[1])
            l = l +2
            continue

        if len(w[0]) == 4:
            outfile.write("<U"+w[0]+">     " + hexword + " " + w[1] + "\n")
        else:
            outfile.write("<U000"+w[0]+">     " + hexword + " " + w[1] + "\n")
        l = l +1

''' Function to convert Unicode characters to /x**/x**/x**  format.
'''
def convert_to_hex(unihex):
    length_hex = len(unihex)
    hexword = ""
    for i in range(0, length_hex):
        hexword =hexword + "/x" + ('%02x' %unihex[i])
    return hexword

def write_comments(outfile, flag):
    if flag == 0:
        outfile.write("<code_set_name> UTF-8\n")
        outfile.write("<comment_char> %\n")
        outfile.write("<escape_char> /\n")
        outfile.write("<mb_cur_min> 1\n")
        outfile.write("<mb_cur_max> 6\n\n")
        outfile.write("% CHARMAP generated using utf8-gen.py\n")
        outfile.write("% alias ISO-10646/UTF-8\n")
        outfile.write("CHARMAP\n")
    if flag == 1:
        outfile.write("% Character width according to Unicode 7.0.0.\n")
        outfile.write("% - Default width is 1.\n")
        outfile.write("% - Double-width characters have width 2; generated from\n")
        outfile.write("%        \"grep '^[^;]*;[WF]' EastAsianWidth.txt\"\n")
#        outfile.write("%   and  \"grep '^[^;]*;[^WF]' EastAsianWidth.txt\"\n")  -- This is wrong
        outfile.write("% - Non-spacing characters have width 0; generated from PropList.txt or\n")
        outfile.write("%   \"grep '^[^;]*;[^;]*;[^;]*;[^;]*;NSM;' UnicodeData.txt\"\n")
        outfile.write("% - Format control characters have width 0; generated from\n")
        outfile.write("%   \"grep '^[^;]*;[^;]*;Cf;' UnicodeData.txt\"\n")
#       Not needed covered by Cf
#        outfile.write("% - Zero width characters have width 0; generated from\n")
#        outfile.write("%   \"grep '^[^;]*;ZERO WIDTH ' UnicodeData.txt\"\n")
        outfile.write("WIDTH\n")


''' For WIDTH we need to process output from 2 files UnicodeData.txt and EastAsianWidth.txt.
   1. Processing two files and gathering output in elist. 2) copying elist to "temp" file
   2. Sorting with glibc "sort -n"  and copying to sort_temp file.
   3. Copying required things to UTF-8 file
   4. Removing temporary files.
'''
def process_width(outfile, ulines, elines):
    width_dict = {}
    for l in ulines:
        w = l.split(";")
        if w[4]== "NSM" or w[2] == "Cf":
            if len(w[0]) < 5:
                width_dict[int(w[0], 16)] = '<U'+w[0]+'>\t0'
            else:
                width_dict[int(w[0], 16)] = '<U000'+w[0]+'>\t0'

    for l in elines:
        # If an entry in EastAsianWidth.txt is found, it overrides entries in
        # UnicodeData.txt:
        w = l.split(";")
        if not '..' in w[0]:
            if len(w[0]) == 4:
                width_dict[int(w[0], 16)] = '<U'+w[0]+'>\t2'
            else:
                width_dict[int(w[0], 16)] = '<U000'+w[0]+'>\t2'
        else:
            wc = w[0].split("..")
            for key in range(int(wc[0], 16), int(wc[1], 16)+1):
                if  key in width_dict:
                    del width_dict[key]
            if len(wc[0]) == 4:
                width_dict[int(wc[0], 16)] = '<U'+wc[0]+'>...<U'+wc[1]+'>\t2'
            else:
                width_dict[int(wc[0], 16)] = '<U000'+wc[0]+'>...<U000'+wc[1]+'>\t2'

    for l in sorted(width_dict):
        outfile.write(width_dict[l]+'\n')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: python3 utf8-gen.py UnicodeData.txt EastAsianWidth.txt")
    else:
        unidata_file = open(sys.argv[1])
        easta_file = open(sys.argv[2])
        outfile=open("UTF-8","w")
        flines = unidata_file.readlines()

        # Processing UnicodeData.txt and write CHARMAP to UTF-8 file
        write_comments(outfile, 0)
        process_charmap(flines, outfile)
        outfile.write("END CHARMAP\n\n")

        # Processing EastAsianWidth.txt and write WIDTH to UTF-8 file
        write_comments(outfile, 1)
        elines = []
        for line in easta_file.readlines():
	    # Reserved characters of EastAasianWidth do not appear in charmap and produce "Unknown Character" error.
            if re.match(r'.*<reserved-.+>\.\.<reserved-.+>.*', line):
                    continue
            if re.match(r'^[^;]*;[WF]', line):
                    elines.append(line.strip())
        process_width(outfile, flines, elines)
        outfile.write("END WIDTH\n")

        outfile.close()
        unidata_file.close()
