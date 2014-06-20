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
               print "uppercase @ ", i
	       outfile.write("upper \\\n")
	       write_class(i+3, outfile, flines)

	    if (l.split()[3] == "Lowercase") and (l.split()[2] == "Property:"):
               print "lowercase @ ", i
	       outfile.write("lower \\\n")
	       write_class(i+3, outfile, flines)

	    if (l.split()[3] == "Alphabetic") and (l.split()[2] == "Property:"):
               print "alphabetic @ ", i
	       outfile.write("alpha \\\n")
	       write_class(i+3, outfile, flines)
        i = i+1

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
#         print x
	    break
	if len(flines[x].split()[0].split(".."))==1:
#            print flines[x].split()[0].split("..")
	    outfile.write( "<U"  + flines[x].split()[0].split("..")[0] + ">;")
            nline_count = nline_count + 1
	else:
#         print flines[x].split()[0].split("..")
	    outfile.write( "<U"  + flines[x].split()[0].split("..")[0] + ">..<U" + flines[x].split()[0].split("..")[1] + ">;")
            if len(flines[x].split()[0].split("..")[0]) > 4:
                nline_count = nline_count + 3
            else:
                nline_count = nline_count + 2
    outfile.write("\n")
		   
		



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print  " USAGE: python gen-unicode-ctype-dcp.py DerivedCoreProperties.txt VERSION "
    else:
        dcp_file = sys.argv[1]
        outfile=open("unicode-ctype.txt","w")
        outfile.write("% Generated automatically by gen-unicode-ctype-dcp for Unicode " + sys.argv[2] + "\n")
        outfile.write("LC_CTYPE\n")
	process_dcp(dcp_file, outfile)
