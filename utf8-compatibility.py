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

# Dictionary holding the entire contents of the UnicodeData.txt file
#
# Contents of this dictionary look like this:
#
# {0: {'category': 'Cc',
#      'title': None,
#      'digit': '',
#      'name': '<control>',
#      'bidi': 'BN',
#      'combining': '0',
#      'comment': '',
#      'oldname': 'NULL',
#      'decomposition': '',
#      'upper': None,
#      'mirrored': 'N',
#      'lower': None,
#      'decdigit': '',
#      'numeric': ''},
#      …
# }
unicode_attributes = {}

# Dictionary holding the entire contents of the EastAsianWidths.txt file
#
# Contents of this dictionary look like this:
#
# {0: 'N', … , 45430: 'W', …}
east_asian_widths = {}

def fill_attribute(code_point, fields):
    '''Stores in unicode_attributes[code_point] the values from the fields.

    One entry in the unicode_attributes dictionary represents one line
    in the UnicodeData.txt file.

    '''
    unicode_attributes[code_point] =  {
        'name': fields[1],          # Character name
        'category': fields[2],      # General category
        'combining': fields[3],     # Canonical combining classes
        'bidi': fields[4],          # Bidirectional category
        'decomposition': fields[5], # Character decomposition mapping
        'decdigit': fields[6],      # Decimal digit value
        'digit': fields[7],         # Digit value
        'numeric': fields[8],       # Numeric value
        'mirrored': fields[9],      # mirrored
        'oldname': fields[10],      # Old Unicode 1.0 name
        'comment': fields[11],      # comment
        'upper': int(fields[12], 16) if fields[12] else None, # Uppercase mapping
        'lower': int(fields[13], 16) if fields[13] else None, # Lowercase mapping
        'title': int(fields[14], 16) if fields[14] else None, # Titlecase mapping
    }

def fill_attributes(filename):
    '''Stores the entire contents of the UnicodeData.txt file
    in the unicode_attributes dictionary.

    A typical line for a single code point in UnicodeData.txt looks
    like this:

    0041;LATIN CAPITAL LETTER A;Lu;0;L;;;;;N;;;;0061;

    Code point ranges are indicated by pairs of lines like this:

    4E00;<CJK Ideograph, First>;Lo;0;L;;;;;N;;;;;
    9FCC;<CJK Ideograph, Last>;Lo;0;L;;;;;N;;;;;
    '''
    with open(filename, mode='r') as file:
        fields_start = []
        for line in file:
            fields = line.strip().split(';')
            if len(fields) != 15:
                sys.stderr.write(
                    'short line in file "%(f)s": %(l)s\n' %{
                    'f': filename, 'l': line})
                exit(1)
            if fields[2] == 'Cs':
                # Surrogates are UTF-16 artefacts,
                # not real characters. Ignore them.
                fields_start = []
                continue
            if fields[1].endswith(', First>'):
                fields_start = fields
                fields_start[1] = fields_start[1].split(',')[0][1:]
                continue
            if fields[1].endswith(', Last>'):
                fields[1] = fields[1].split(',')[0][1:]
                if fields[1:] != fields_start[1:]:
                    sys.stderr.write(
                        'broken code point range in file "%(f)s": %(l)s\n' %{
                            'f': filename, 'l': line})
                    exit(1)
                for code_point in range(
                        int(fields_start[0], 16),
                        int(fields[0], 16)+1):
                    fill_attribute(code_point, fields)
                fields_start = []
                continue
            fill_attribute(int(fields[0], 16), fields)
            fields_start = []

def fill_east_asian_widths(filename):
    with open(filename, mode='r') as file:
        for line in file:
            match = re.match(
                r'^(?P<codepoint1>[0-9A-F]{4,6})'
                +r'(?:\.\.(?P<codepoint2>[0-9A-F]{4,6}))?'
                +r'\s*;\s*(?P<property>[a-zA-Z]+)',
                line)
            if not match:
                continue
            start = match.group('codepoint1')
            end = match.group('codepoint2')
            if not end:
                end = start
            for code_point in range(int(start, 16), int(end, 16)+1):
                east_asian_widths[code_point] = match.group('property')

def ucs_symbol(code_point):
    if code_point < 0x10000:
        return '<U{:04X}>'.format(code_point)
    else:
        return '<U{:08X}>'.format(code_point)

def create_charmap_dictionary(file_name):
    with open(file_name, mode='r') as file:
        charmap_dictionary = {}
        for line in file:
            if line.startswith('CHARMAP'):
                break
        for line in file:
            if line.startswith('END CHARMAP'):
                return charmap_dictionary
            if line.startswith('%'):
                continue
            match = re.match(
                r'^<U(?P<codepoint1>[0-9A-F]{4,8})>'
                +r'(:?\.\.<U(?P<codepoint2>[0-9-A-F]{4,8})>)?'
                +r'\s+(?P<hexutf8>(/x[0-9a-f]{2}){1,4})',
                line)
            if not match:
                continue
            codepoint1 = match.group('codepoint1')
            codepoint2 = match.group('codepoint2')
            if not codepoint2:
                codepoint2 = codepoint1
            for i in range(int(codepoint1, 16),
                           int(codepoint2, 16) + 1):
                charmap_dictionary[i] = match.group('hexutf8')
        sys.stderr.write('No “CHARMAP” or no “END CHARMAP” found in %s\n' %file_name)
        exit(1)

def check_charmap(original_file_name, new_file_name):
    print('************************************************************')
    print('Report on CHARMAP:')
    global args
    ocharmap = create_charmap_dictionary(original_file_name)
    ncharmap = create_charmap_dictionary(new_file_name)
    changed_charmap = {}
    for key in set(ocharmap).intersection(set(ncharmap)):
        if ocharmap[key] != ncharmap[key]:
            changed_charmap[key] = (ocharmap[key], ncharmap[key])
    print('Total removed characters in newly generated CHARMAP: %d'
          %len(set(ocharmap)-set(ncharmap)))
    if args.show_missing_characters:
        for key in sorted(set(ocharmap)-set(ncharmap)):
            print('removed: {:s}     {:s} {:s}'.format(
                ucs_symbol(key),
                ocharmap[key],
                unicode_attributes[key]['name'] if key in unicode_attributes else None))
    print('Total changed characters in newly generated CHARMAP: %d'
          %len(changed_charmap))
    if args.show_changed_characters:
        for key in sorted(changed_charmap):
            print('changed: {:s}     {:s}->{:s} {:s}'.format(
                ucs_symbol(key),
                changed_charmap[key][0],
                changed_charmap[key][1],
                unicode_attributes[key]['name'] if key in unicode_attributes else None))
    print('Total added characters in newly generated CHARMAP: %d'
          %len(set(ncharmap)-set(ocharmap)))
    if args.show_added_characters:
        for key in sorted(set(ncharmap)-set(ocharmap)):
            print('added: {:s}     {:s} {:s}'.format(
                ucs_symbol(key),
                ncharmap[key],
                unicode_attributes[key]['name'] if key in unicode_attributes else None))

def create_width_dictionary(file_name):
    with open(file_name, mode='r') as file:
        width_dictionary = {}
        for line in file:
            if line.startswith('WIDTH'):
                break
        for line in file:
            if line.startswith('END WIDTH'):
                return width_dictionary
            match = re.match(
                r'^<U(?P<codepoint1>[0-9A-F]{4,8})>'
                +r'(:?\.\.\.<U(?P<codepoint2>[0-9-A-F]{4,8})>)?'
                +r'\s+(?P<width>[02])',
                line)
            if not match:
                continue
            codepoint1 = match.group('codepoint1')
            codepoint2 = match.group('codepoint2')
            if not codepoint2:
                codepoint2 = codepoint1
            for i in range(int(codepoint1, 16),
                           int(codepoint2, 16) + 1):
                width_dictionary[i] = int(match.group('width'))
        sys.stderr.write('No “WIDTH” or no “END WIDTH” found in %s\n' %file)

def check_width(original_file_name, new_file_name):
    print('************************************************************')
    print('Report on WIDTH:')
    global args
    owidth = create_width_dictionary(original_file_name)
    nwidth = create_width_dictionary(new_file_name)
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
    check_charmap(args.old_utf8_file, args.new_utf8_file)
    check_width(args.old_utf8_file, args.new_utf8_file)
