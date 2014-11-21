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
# USAGE: python3 utf8-compatibility.py -o ../glibc/localedata/charmaps/UTF-8 -n UTF-8  -m -a -u unicode7-0/UnicodeData.txt -e unicode7-0/EastAsianWidth.txt
# For issues upstream https://github.com/pravins/glibc-i18n

import sys
import re
import argparse

global args

unicode_attributes = {}
east_asian_widths = {}

def fill_attribute(code_point, fields):
    unicode_attributes[code_point] =  {
        'name': fields[1],
        'category': fields[2],
        'combining': fields[3],
        'bidi': fields[4],
        'decomposition': fields[5],
        'decdigit': fields[6],
        'digit': fields[7],
        'numeric': fields[8],
        'mirrored': fields[9],
        'oldname': fields[10],
        'comment': fields[11],
        'upper': int(fields[12], 16) if fields[12] else None,
        'lower': int(fields[13], 16) if fields[13] else None,
        'title': int(fields[14], 16) if fields[14] else None,
    }

def fill_attributes(filename):
    with open(filename, mode='r') as file:
        lines = file.readlines()
        for lineno in range(0, len(lines)):
            fields = lines[lineno].strip().split(';')
            if len(fields) != 15:
                sys.stderr.write(
                    'short line in file "%(f)s": %(l)s\n' %{
                    'f': filename, 'l': lines[lineno]})
                exit(1)
            if fields[2] == 'Cs':
                # Surrogates are UTF-16 artefacts,
                # not real characters. Ignore them.
                continue
            if fields[1].endswith(', Last>'):
                continue
            if fields[1].endswith(', First>'):
                fields[1] = fields[1].split(',')[0][1:]
                fields_end = lines[lineno+1].split(';')
                if (not fields_end[1].endswith(', Last>')
                    or len(fields_end) != 15):
                    sys.stderr.write(
                        'missing end range in file "%(f)s": %(l)s\n' %{
                        'f': filename, 'l': lines[lineno+1]})
                for code_point in range(
                        int(fields[0], 16),
                        int(fields_end[0], 16)+1):
                    fill_attribute(code_point, fields)
            fill_attribute(int(fields[0], 16), fields)

def fill_east_asian_widths(filename):
    with open(filename, mode='r') as file:
        for line in file:
            match = re.match(
                r'^(?P<codepoint>[0-9A-F]{4,6})\s*;\s*(?P<property>[a-zA-Z]+)',
                line)
            if match:
                east_asian_widths[
                        int(match.group('codepoint'), 16)
                ] = match.group('property')
            match = re.match(
                r'^(?P<codepoint1>[0-9A-F]{4,6})\.\.(?P<codepoint2>[0-9A-F]{4,6})\s*;\s*(?P<property>[a-zA-Z]+)',
                line)
            if match:
                for code_point in range(
                        int(match.group('codepoint1'), 16),
                        int(match.group('codepoint2'), 16)+1):
                    east_asian_widths[code_point] = match.group('property')

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
    changed_width = {}
    for key in owidth:
        if key in nwidth and owidth[key] != nwidth[key]:
            changed_width[key] = (owidth[key], nwidth[key])
    for key in owidth:
        if key not in nwidth:
            changed_width[key] = (owidth[key], 1)
    for key in nwidth:
        if key not in owidth:
            changed_width[key] = (1, nwidth[key])
    print("Total changed characters in newly generated WIDTH: ", len(changed_width))
    if args.show_changed_characters:
        for key in sorted(changed_width):
            print('changed width: 0x%04x : %d->%d eaw=%s category=%2s bidi=%-3s name=%s'
                  %(key,
                    changed_width[key][0],
                    changed_width[key][1],
                    east_asian_widths[key] if key in east_asian_widths else None,
                    unicode_attributes[key]['category'] if key in unicode_attributes else None,
                    unicode_attributes[key]['bidi'] if key in unicode_attributes else None,
                    unicode_attributes[key]['name'] if key in unicode_attributes else None,
            ))
    mwidth = dict(set(owidth.items()) - set(nwidth.items()))
    print("Total missing characters in newly generated WIDTH: ", len(mwidth))
    if args.show_missing_characters:
        for key in sorted(mwidth):
            print('removed: 0x%04x : %d eaw=%s category=%2s bidi=%-3s name=%s'
                  %(key,
                    mwidth[key],
                    east_asian_widths[key] if key in east_asian_widths else None,
                    unicode_attributes[key]['category'] if key in unicode_attributes else None,
                    unicode_attributes[key]['bidi'] if key in unicode_attributes else None,
                    unicode_attributes[key]['name'] if key in unicode_attributes else None,
            ))
    awidth = dict(set(nwidth.items()) - set(owidth.items()))
    print("Total added characters in newly generated WIDTH: ", len(awidth))
    if args.show_added_characters:
        for key in sorted(awidth):
            print('added: 0x%04x : %d eaw=%s category=%2s bidi=%-3s name=%s'
                  %(key,
                    awidth[key],
                    east_asian_widths[key] if key in east_asian_widths else None,
                    unicode_attributes[key]['category'] if key in unicode_attributes else None,
                    unicode_attributes[key]['bidi'] if key in unicode_attributes else None,
                    unicode_attributes[key]['name'] if key in unicode_attributes else None,
            ))

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
    parser.add_argument('-u', '--unicode_data_file',
                        nargs='?',
                        type=str,
                        help='The UnicodeData.txt file to read.')
    parser.add_argument('-e', '--east_asian_width_file',
                        nargs='?',
                        type=str,
                        help='The EastAsianWidth.txt file to read.')
    parser.add_argument('-a', '--show_added_characters',
                        action='store_true',
                        help='Show characters which were added in detail.')
    parser.add_argument('-m', '--show_missing_characters',
                        action='store_true',
                        help='Show characters which were removed in detail.')
    parser.add_argument('-c', '--show_changed_characters',
                        action='store_true',
                        help='Show characters whose width was changed in detail.')
    global args
    args = parser.parse_args()

    if args.unicode_data_file:
        fill_attributes(args.unicode_data_file)
    if args.east_asian_width_file:
        fill_east_asian_widths(args.east_asian_width_file)
    # o_ for Original UTF-8 and n_ for New UTF-8 file
    o_lines = open(args.old_utf8_file).readlines()
    n_lines = open(args.new_utf8_file).readlines()
    print("Report on CHARMAP:")
    check_charmap(o_lines, n_lines)
    print("************************************************************\n")
    print("Report on WIDTH:")
    check_width(o_lines, n_lines)
