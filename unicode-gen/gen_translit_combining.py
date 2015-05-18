#!/usr/bin/python3
#
# Generate a translit_combining file from a UnicodeData file.
# Copyright (C) 2015 Free Software Foundation, Inc.
# This file is part of the GNU C Library.
#
# The GNU C Library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# The GNU C Library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with the GNU C Library; if not, see
# <http://www.gnu.org/licenses/>.

'''
Generate a translit_combining file from UnicodeData.txt

To see how this script is used, call it with the “-h” option:

    $ ./gen_translit_combining -h
    … prints usage message …
'''

import argparse
import time
import unicode_utils

def read_input_file(filename):
    '''Reads the original glibc translit_combining file to get the
    original head and tail.

    We want to replace only the part of the file between
    “translit_start” and “translit_end”
    '''
    head = tail = ''
    with open(filename, mode='r') as translit_file:
        for line in translit_file:
            head = head + line
            if line.startswith('translit_start'):
                break
        for line in translit_file:
            if line.startswith('translit_end'):
                tail = line
                break
        for line in translit_file:
            tail = tail + line
    return (head, tail)

def output_head(translit_file, unicode_version, head=''):
    '''Write the header of the output file, i.e. the part of the file
    before the “translit_start” line.
    '''
    if ARGS.input_file and head:
        translit_file.write(head)
    else:
        translit_file.write('escape_char /\n')
        translit_file.write('comment_char %\n')
        translit_file.write('\n')
        translit_file.write('% Transliterations that remove all ')
        translit_file.write('combining characters (accents,\n')
        translit_file.write('% pronounciation marks, etc.).\n')
        translit_file.write('% Generated automatically from UnicodeData.txt '
                        + 'by gen_translit_combining.py '
                        + 'on {:s} '.format(time.strftime('%Y-%m-%d'))
                        + 'for Unicode {:s}.\n'.format(unicode_version))
        translit_file.write('\n')
        translit_file.write('LC_CTYPE\n')
        translit_file.write('\n')
        translit_file.write('translit_start\n')

def output_tail(translit_file, tail=''):
    '''Write the tail of the output file'''
    if ARGS.input_file and tail:
        translit_file.write(tail)
    else:
        translit_file.write('translit_end\n')
        translit_file.write('\n')
        translit_file.write('END LC_CTYPE\n')

def is_combining_remove(code_point):
    '''Check whether this is a combining character which should be listed
    in the section of the translit_combining file where combining
    characters are replaced by empty strings.

    We ignore combining characters from many scripts here because
    the original translit_combining file didn’t do this for the
    combining characters from these scripts either and I am not
    sure yet whether this would be useful to do for all combining
    characters or not. For the moment I think it is better to keep
    close to the spirit of the original file.
    '''
    if not unicode_utils.is_combining(code_point):
        return False
    name = unicode_utils.UNICODE_ATTRIBUTES[code_point]['name']
    for substring in ('DEVANAGARI',
                      'BENGALI',
                      'CYRILLIC',
                      'SYRIAC',
                      'THAANA',
                      'NKO',
                      'GURMUKHI',
                      'TAMIL',
                      'GUJARATI',
                      'ORIYA',
                      'TELUGU',
                      'KANNADA',
                      'MALAYALAM',
                      'SINHALA',
                      'THAI',
                      'LAO',
                      'TIBETAN',
                      'MYANMAR',
                      'ETHIOPIC',
                      'TAGALOG',
                      'HANUNOO',
                      'BUHID',
                      'TAGBANWA',
                      'KHMER',
                      'MONGOLIAN',
                      'LIMBU',
                      'NEW TAI LUE',
                      'BUGINESE',
                      'BALINESE',
                      'SUNDANESE',
                      'LEPCHA',
                      'IDEOGRAPHIC',
                      'HANGUL',
                      'SYLOTI',
                      'SAURASHTRA',
                      'KAYAH',
                      'REJANG',
                      'CHAM',
                      'VARIATION SELECTOR',
                      'KHAROSHTHI',
                      'MUSICAL SYMBOL',
                      'SAMARITAN',
                      'MANDAIC',
                      'TAI THAM',
                      'BATAK',
                      'VEDIC',
                      'COPTIC',
                      'TIFINAGH',
                      'BAMUM',
                      'JAVANESE',
                      'TAI VIET',
                      'MEETEI',
                      'MANICHAEAN',
                      'BRAHMI',
                      'KAITHI',
                      'CHAKMA',
                      'MAHAJANI',
                      'SHARADA',
                      'KHOJKI',
                      'KHUDAWADI',
                      'GRANTHA',
                      'TIRHUTA',
                      'SIDDHAM',
                      'MODI VOWEL',
                      'MODI SIGN',
                      'TAKRI',
                      'BASSA VAH',
                      'PAHAWH HMONG',
                      'MIAO',
                      'DUPLOYAN',
                      'MENDE KIKAKUI'
    ):
        if substring in name:
            return False
    return True

def canonical_decompose(code_point):
    '''http://www.unicode.org/reports/tr44/#Character_Decomposition_Mappings

    In some instances a canonical mapping or a compatibility mapping
    may consist of a single character. For a canonical mapping, this
    indicates that the character is a canonical equivalent of another
    single character. For a compatibility mapping, this indicates that
    the character is a compatibility equivalent of another single
    character.

    A canonical mapping may also consist of a pair of characters, but
    is never longer than two characters. When a canonical mapping
    consists of a pair of characters, the first character may itself
    be a character with a decomposition mapping, but the second
    character never has a decomposition mapping.

    We ignore the canonical decomposition for code points
    matching certain substrings because the original translit_combining
    file didn’t include these types of characters either. I am unsure
    about the usefulness of including them and want to keep close
    to the spirit of the original file for the moment.
    '''
    name = unicode_utils.UNICODE_ATTRIBUTES[code_point]['name']
    for substring in ('MUSICAL SYMBOL',
                      'CJK COMPATIBILITY IDEOGRAPH',
                      'BALINESE',
                      'KAITHI LETTER',
                      'CHAKMA VOWEL',
                      'GRANTHA VOWEL',
                      'TIRHUTA VOWEL',
                      'SIDDHAM VOWEL'):
        if substring in name:
            return []
    decomposition = unicode_utils.UNICODE_ATTRIBUTES[
        code_point]['decomposition']
    if decomposition and not decomposition.startswith('<'):
        decomposed_code_points = [int(x, 16) for x in decomposition.split(' ')]
        if decomposed_code_points:
            cd0 = canonical_decompose(decomposed_code_points[0])
            if cd0:
                decomposed_code_points = cd0 + decomposed_code_points[1:]
        return decomposed_code_points
    else:
        return []

def special_decompose(code_point_list):
    '''
    Decompositions which are not canonical or which are not in
    UnicodeData.txt at all but some of these were used in the original
    translit_combining file in glibc and they seemed to make sense.
    I want to keep the update of translit_combining close to the
    spirit of the original file, therefore I added these special
    decomposition rules here.
    '''
    special_decompose_dict = {
        # Don’t add stuff like ø → o, đ → d, ... here,
        # this should be manually added to translit_neutral instead
        # Don’t add ligatures like æ → ae, ... here,
        # they should be in translit_compat
        (0x00E6,): [0x0061, 0x0065], # æ → ae
        (0x00C6,): [0x0041, 0x0045], # Æ → AE
        (0x05F2,): [0x05D9, 0x05D9], # ײ → יי
        # 0x2002 has a <compat> decomposition to 0x0020 in UnicodeData.txt
        (0x2002,): [0x0020], # EN SPACE → SPACE
        # 0x2003 has a <compat> decomposition to 0x0020 in UnicodeData.txt
        (0x2003,): [0x0020], # EM SPACE → SPACE
        # Special rule for 〈 U+3008 is added
        # because 〉 U+2329 has the canonical decomposition U+3008
        # and we want to further decompose this to > U+003C.
        (0x3008,): [0x003C], # 〈 → <
        # Special rule for 〉 U+3009 is added
        # because 〉 U+232A has the canonical decomposition U+3009
        # and we want to further decompose this to < U+003E.
        (0x3009,): [0x003E], # 〉→ >
    }
    if tuple(code_point_list) in special_decompose_dict:
        return special_decompose_dict[tuple(code_point_list)]
    else:
        return code_point_list

def output_combining_remove(translit_file):
    '''Write the section of the translit_combining file where combining
    characters are replaced by empty strings.
    '''
    translit_file.write('\n')
    for code_point in sorted(unicode_utils.UNICODE_ATTRIBUTES):
        name = unicode_utils.UNICODE_ATTRIBUTES[code_point]['name']
        if is_combining_remove(code_point):
            translit_file.write('% {:s}\n'.format(name))
            translit_file.write('{:s} ""\n'.format(
                unicode_utils.ucs_symbol(code_point)))
    translit_file.write('\n')

def output_decompositions(translit_file):
    '''Write the section of the translit_combining file where characters
    characters are decomposed and combining characters stripped from
    the decompositions.
    '''
    for code_point in sorted(unicode_utils.UNICODE_ATTRIBUTES):
        decomposed_code_points = [canonical_decompose(code_point)]
        decomposed_code_points[0] = [x for x in decomposed_code_points[0]
                             if not is_combining_remove(x)]
        if not decomposed_code_points[0]:
            if special_decompose([code_point]) != [code_point]:
                decomposed_code_points[0] = special_decompose([code_point])
        else:
            special_decomposed_code_points = []
            for decomposed_code_point in decomposed_code_points[0]:
                special_decomposed_code_points += special_decompose(
                    [decomposed_code_point])
            if (special_decomposed_code_points
                != decomposed_code_points[0]):
                decomposed_code_points.append(
                    special_decomposed_code_points)
        if decomposed_code_points[0]:
            translit_file.write('% {:s}\n'.format(
                unicode_utils.UNICODE_ATTRIBUTES[code_point]['name']))
            translit_file.write('{:s} '.format(
                unicode_utils.ucs_symbol(code_point)))
            for index in range(0, len(decomposed_code_points)):
                if index > 0:
                    translit_file.write(';')
                if len(decomposed_code_points[index]) > 1:
                    translit_file.write('"')
                for decomposed_code_point in decomposed_code_points[index]:
                    translit_file.write('{:s}'.format(
                        unicode_utils.ucs_symbol(decomposed_code_point)))
                if len(decomposed_code_points[index]) > 1:
                    translit_file.write('"')
            translit_file.write('\n')
    translit_file.write('\n')

def output_transliteration(translit_file):
    '''Write the new transliteration to the output file'''
    output_combining_remove(translit_file)
    output_decompositions(translit_file)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='''
        Generate a translit_combining file from UnicodeData.txt.
        ''')
    PARSER.add_argument(
        '-u', '--unicode_data_file',
        nargs='?',
        type=str,
        default='UnicodeData.txt',
        help=('The UnicodeData.txt file to read, '
              + 'default: %(default)s'))
    PARSER.add_argument(
        '-i', '--input_file',
        nargs='?',
        type=str,
        help=''' The original glibc/localedata/locales/translit_combining
        file.''')
    PARSER.add_argument(
        '-o', '--output_file',
        nargs='?',
        type=str,
        default='translit_combining.new',
        help='''The new translit_combining file, default: %(default)s.  If the
        original glibc/localedata/locales/translit_combining file has
        been given as an option, the header up to the
        “translit_start” line and the tail from the “translit_end”
        line to the end of the file will be copied unchanged into the
        output file.  ''')
    PARSER.add_argument(
        '--unicode_version',
        nargs='?',
        required=True,
        type=str,
        help='The Unicode version of the input files used.')
    ARGS = PARSER.parse_args()

    unicode_utils.fill_attributes(ARGS.unicode_data_file)
    HEAD = TAIL = ''
    if ARGS.input_file:
        (HEAD, TAIL) = read_input_file(ARGS.input_file)
    with open(ARGS.output_file, mode='w') as TRANSLIT_FILE:
        output_head(TRANSLIT_FILE, ARGS.unicode_version, head=HEAD)
        output_transliteration(TRANSLIT_FILE)
        output_tail(TRANSLIT_FILE, tail=TAIL)
