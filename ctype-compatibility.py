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
# USAGE: python ctype-compatibility.py existing_ctype_file new_ctype_file
# Existing LC_CTYPE file /usr/share/i18n/locale/i18n and new generated 'unicode-ctype'

import os
import sys
import re
import unicodedata
import argparse

def get_lines_from_file(filename):
    '''Get all non-comment lines from a file

    Also merge all lines which are continued on the next line because
    they end in “/” into a single line.
    '''
    all_lines = []
    with open(filename) as file:
        current_line = ''
        for line in file:
            line = line.strip('\n')
            if '%' in line:
                if line.endswith('/'):
                    line = line[0:line.find('%')] + '/'
                else:
                    line = line[0:line.find('%')]
            line = line.strip()
            if line.endswith('/'):
                current_line += line[:-1]
            else:
                all_lines.append(current_line + line)
                current_line = ''
    return all_lines

def extract_character_classes_and_code_points(filename):
    '''Get all Unicode code points for each character class from a file

    Store these code points in a dictionary using the character classes
    as keys and the list of code points in this character class as values.

    In case  of the character classes “toupper”, “tolower”, and “totitle”,
    these area actually pairs of code points
    '''
    ctype_dict = {}
    for line in get_lines_from_file(filename):
        for char_class in [
                'upper',
                'lower',
                'alpha',
                'digit',
                'space',
                'cntrl',
                'punct',
                'graph',
                'print',
                'xdigit',
                'blank',
                'combining',
                'combining_level3',
                'toupper',
                'tolower',
                'totitle']:
            match = re.match(r'^(?:(?:class|map)\s+")?'
                             +char_class+
                             '(?:";)?\s+', line)
            if match:
                if char_class not in ctype_dict:
                    ctype_dict[char_class] = []
                process_chars(
                    ctype_dict[char_class],
                    line[match.end():])
    return ctype_dict

def process_chars(char_class_list, code_point_line):
    '''
    Extract Unicode values from code_point_line
    and add to the list of code points in a character class
    '''
    for code_points in code_point_line.split(';'):
        code_points = code_points.strip()
        match = re.match(r'^<U(?P<codepoint>[0-9A-F]{4,8})>$', code_points)
        if match: # <UXXXX>
            char_class_list.append(
                int(match.group('codepoint'), 16))
            continue
        match = re.match(
            r'^<U(?P<codepoint1>[0-9A-F]{4,8})>'
            +'\.\.'+
            '<U(?P<codepoint2>[0-9A-F]{4,8})>$',
            code_points)
        if match: # <UXXXX>..<UXXXX>
            for codepoint in range(
                    int(match.group('codepoint1'), 16),
                    int(match.group('codepoint2'), 16) + 1):
                char_class_list.append(codepoint)
            continue
        match = re.match(
            r'^<U(?P<codepoint1>[0-9A-F]{4,8})>'
            +'\.\.\(2\)\.\.'+
            '<U(?P<codepoint2>[0-9A-F]{4,8})>$',
            code_points)
        if match: # <UXXXX>..(2)..<UXXXX>
            for codepoint in range(
                    int(match.group('codepoint1'), 16),
                    int(match.group('codepoint2'), 16) + 1,
                    2):
                char_class_list.append(codepoint)
            continue
        match = re.match(
            r'^\('
            +'<U(?P<codepoint1>[0-9A-F]{4,8})>'
            +','+
            '<U(?P<codepoint2>[0-9A-F]{4,8})>'
            +'\)$',
            code_points)
        if match: # (<UXXXX>,<UXXXX>)
            char_class_list.append((
                int(match.group('codepoint1'), 16),
                int(match.group('codepoint2'), 16)))
            continue

def compare_lists(old_ctype_dict, new_ctype_dict):
    for char_class in sorted(old_ctype_dict):
        print("%s: %d chars in old ctype and %d chars in new ctype" %(
            char_class,
            len(old_ctype_dict[char_class]),
            len(new_ctype_dict[char_class])))
        report(char_class,
               old_ctype_dict[char_class],
               new_ctype_dict[char_class])

def report_code_points(char_class, code_point_list, text=''):
   for code_point in sorted(code_point_list):
       if type(code_point) == type(int()):
           print('%(char_class)s: %(text)s: %(char)s %(code_point)s %(name)s' %{
               'text': text,
               'char': chr(code_point),
               'char_class': char_class,
               'code_point': hex(code_point),
               'name': unicodedata.name(chr(code_point), 'name unknown')})
       else:
           print('%(char_class)s: %(text)s: %(char0)s → %(char1)s %(code_point0)s → %(code_point1)s %(name0)s → %(name1)s' %{
               'text': text,
               'char_class': char_class,
               'char0': chr(code_point[0]),
               'code_point0': hex(code_point[0]),
               'name0': unicodedata.name(chr(code_point[0]), 'name unknown'),
               'char1': chr(code_point[1]),
               'code_point1': hex(code_point[1]),
               'name1': unicodedata.name(chr(code_point[1]), 'name unknown')
           })

def report(char_class, old_list, new_list):
   print("****************************************************")
   missing_chars = list(set(old_list)-set(new_list))
   print("%(char_class)s: Missing %(number)d characters of old ctype in new ctype " %{
       'char_class': char_class, 'number': len(missing_chars)})
   report_code_points(char_class, missing_chars, 'Missing')
   added_chars = list(set(new_list)-set(old_list))
   print("%(char_class)s: Added %(number)d characters in new ctype which were not in old ctype" %{
       'char_class': char_class, 'number': len(added_chars)})
   report_code_points(char_class, added_chars, 'Added')
   print("----------------------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Check compatibility of ctype file.')
    parser.add_argument('-o', '--old_ctype_file',
                        nargs='?',
                        type=str,
                        default='i18n',
                        help='The old ctype file, default: %(default)s')
    parser.add_argument('-n', '--new_ctype_file',
                        nargs='?',
                        type=str,
                        default='unicode-ctype',
                        help='The new ctype file, default: %(default)s')
    args = parser.parse_args()

    file_i18n = args.old_ctype_file
    file_unicode = args.new_ctype_file
    old_ctype_dict = extract_character_classes_and_code_points(file_i18n)
    new_ctype_dict = extract_character_classes_and_code_points(file_unicode)
    compare_lists(old_ctype_dict, new_ctype_dict)
