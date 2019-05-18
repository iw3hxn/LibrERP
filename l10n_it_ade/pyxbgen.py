#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyxbgen
# Agenzia delle Entrate pyxb generator
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2019 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
import os
import sys
import re

__version__ = '0.1.5.2'


def wash_source(lines, kind):
    lineno = 0
    # TODO: patch fatturapa for OCA compatibility, may not work in the future
    RULES = ('RateType',
             'PesoType',
             'QuantitaType',
             'Amount8DecimalType',
             'Amount2DecimalType',
             'class',
             'rate_type_1',
             'rate_type_2',
             'rate_type_3',
             'rate_type_4',
             'rate_type_5',
             'rate_type_6',
             )
    RULES_START = {
        'RateType': 'class RateType',
        'PesoType': 'class PesoType',
        'QuantitaType': 'class QuantitaType',
        'Amount8DecimalType': 'class Amount8DecimalType',
        'Amount2DecimalType': 'class Amount2DecimalType',
        'class': 'class ',
        'follow': '    ',
        'rate_type_1': 'RateType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive',
        'rate_type_3': 'RateType._InitializeFacetMap(RateType._CF_maxInclusive,',
        'rate_type_5': 'RateType._InitializeFacetMap(RateType._CF_pattern,',
    }
    RULES_MATCH = {
        'rate_type_2': "value_datatype=RateType, value=pyxb.binding.datatypes.decimal('100.0')",
        'rate_type_4': 'RateType._CF_pattern)',
        'rate_type_6': 'RateType._CF_maxInclusive)',
    }
    RULES_REPLMNT = {
        'RateType': ('.decimal)', '.string)', True),
        'PesoType': ('.decimal)', '.string)', True),
        'QuantitaType': ('.decimal)', '.string)', True),
        'Amount8DecimalType': ('.decimal)', '.string)', True),
        'Amount2DecimalType': ('.decimal)', '.string)', True),
        'follow': ('.decimal', '.string', 2),
        'rate_type_1': (0, '# ', 1),
        'rate_type_2': (0, '# ', 1),
        'rate_type_3': ('RateType._CF_maxInclusive,', '', 1),
        'rate_type_4': ('', '', 1),
        'rate_type_5': (-1, ')', 1),
        'rate_type_6': (0, '# ', 1),
    }
    RULES_PATCH = {
        'RateType': 1,
    }
    patch = 0
    while lineno < len(lines):
        if not lines[lineno] or not kind:
            pass
        else:
            for rule in RULES:
                if ((rule in RULES_START and
                        lines[lineno].startswith(RULES_START[rule])) or
                        (rule in RULES_MATCH and
                         lines[lineno].find(RULES_MATCH[rule]) >= 0)):
                    if rule in RULES_REPLMNT:
                        src = RULES_REPLMNT[rule][0]
                        tgt = RULES_REPLMNT[rule][1]
                        cond = RULES_REPLMNT[rule][2]
                        if (cond or patch == cond):
                            if src == 0:
                                lines[lineno] = tgt + lines[lineno]
                            elif src == -1:
                                lines[lineno] = lines[lineno][0:-1] + tgt
                            elif lines[lineno].find(src) < 0:
                                patch = 2
                            elif src == '' and tgt == '':
                                lines[lineno - 1] += lines[lineno].strip()
                                del lines[lineno]
                                lineno -= 1
                            else:
                                lines[lineno] = lines[lineno].replace(src, tgt)
                    if rule in RULES_PATCH:
                        patch = RULES_PATCH[rule]
                    else:
                        patch = 0
                    break
        lineno += 1


def robust_source(lines, file_schema):
    if file_schema:
        TXT1_FILE_SCHEMA = '"' + file_schema + '"'
        TXT2_FILE_SCHEMA = "'" + file_schema + "'"
        TXT3_FILE_SCHEMA = '"' + os.path.abspath(file_schema) + '"'
        TXT4_FILE_SCHEMA = "'" + os.path.abspath(file_schema) + "'"
    state = 0
    lineno = 0
    saved_lines = []
    lines.insert(lineno,
                 '# flake8: noqa')
    lineno += 1
    lines.insert(lineno,
                 '# -*- coding: utf-8 -*-')
    lineno += 1
    while lineno < len(lines):
        if state == 3:
            lines.insert(lineno,
                         'except ImportError as err:')
            lineno += 1
            lines.insert(lineno,
                         '    _logger.debug(err)')
            lineno += 1
            lines.insert(lineno, '')
            lineno += 1
            lines.insert(lineno,
                         'SCHEMA_FILE = \'%s\'' % file_schema)
            lineno += 1
            lines.insert(lineno, '')
            lineno += 1
            state = 2
        if not lines[lineno]:
            if state < 2:
                del lines[lineno]
                lineno -= 1
        elif state == 0 and lines[lineno].startswith('# Generated '):
            lineno += 1
            lines.insert(lineno,
                         '# by Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>')
        elif lines[lineno] == '# -*- coding: utf-8 -*-':
            del lines[lineno]
            lineno -= 1
        elif lines[lineno][0:6] == 'import':
            if lines[lineno][0:11] == 'import pyxb':
                if state == 0:
                    lines.insert(lineno,
                                 'import logging')
                    lineno += 1
                    state = 1
                if state == 1:
                    saved_lines.append(lines[lineno])
                    del lines[lineno]
                    lineno -= 1
                elif state == 2:
                    lines.insert(lineno,
                                 'try:')
                    lineno += 1
                    state = 3
                if state == 3:
                    lines[lineno] = '    %s' % lines[lineno]
            elif lines[lineno][0:10] == 'import _cm' or \
                    lines[lineno][0:10] == 'import _ds':
                lines[lineno] = 'from . %s' % lines[lineno]
        elif state == 1:
            lines.insert(lineno,
                         '_logger = logging.getLogger(__name__)')
            lineno += 1
            lines.insert(lineno,
                         'try:')
            lineno += 1
            for saved_line in saved_lines:
                lines.insert(lineno,
                             '    %s' % saved_line)
                lineno += 1
            lines.insert(lineno,
                         'except ImportError as err:')
            lineno += 1
            lines.insert(lineno,
                         '    _logger.debug(err)')
            lineno += 1
            lines.insert(lineno,
                         '')
            lineno += 1
            state = 2
        elif file_schema:
            lines[lineno] = lines[lineno].replace(TXT1_FILE_SCHEMA,
                                                  'SCHEMA_FILE')
            lines[lineno] = lines[lineno].replace(TXT2_FILE_SCHEMA,
                                                  'SCHEMA_FILE')
            lines[lineno] = lines[lineno].replace(TXT3_FILE_SCHEMA,
                                                  'SCHEMA_FILE')
            lines[lineno] = lines[lineno].replace(TXT4_FILE_SCHEMA,
                                                  'SCHEMA_FILE')
        lineno += 1

def correct_future(lines):
    binding_line = ''
    lineno = 0
    state = -1
    while lineno < len(lines):
        if state < 0 and lines[lineno].find('_ImportedBinding__') >= 0:
            binding_line = lines[lineno]
            del lines[lineno]
            lineno -= 1
        elif state < 0 and lines[lineno].find('import') >= 0:
            state = lineno
        elif state >= 0 and binding_line:
            lines.insert(lineno, binding_line)
            binding_line = ''
        lineno += 1

LEX_RULES = {
}

def topep8(lines, file_schema):
    lineno = 0
    prior_left_indent = True
    empty_lines = 0
    token = ''
    while lineno < len(lines):
        # if lines[lineno].find('_GenerationUID = ')>=0:
        #     import pdb
        #     pdb.set_trace()
        # print lineno, lines[lineno]
        if not lines[lineno]:
            empty_lines += 1
            lineno += 1
            continue
        elif lines[lineno].count('(') != lines[lineno].count(')'):
            pass
        elif lines[lineno].count('[') != lines[lineno].count(']'):
            pass
        elif lines[lineno].count('{') != lines[lineno].count('}'):
            pass
        elif lines[lineno][0] == ' ':
            empty_lines = 0
            prior_left_indent = False
        else:
            if (not prior_left_indent and
                    lines[lineno][0:6] != 'except'):
                while empty_lines <= 2:
                    lines.insert(lineno, '')
                    empty_lines += 1
            empty_lines = 0
            prior_left_indent = True
        if lines[lineno] == '#' * len(lines[lineno]):
            del lines[lineno]
            continue
        x = re.match('[ ]*class[ ]+[A-Za-z0-9_]+',
                     lines[lineno])
        if x:
            token = ''
        if token:
            t = ',%s' % token
            x = re.match(t, lines[lineno])
            if x:
                lines[lineno] = lines[lineno].replace(t, '')
            t = ', %s' % token
            x = re.match(t, lines[lineno])
            if x:
                lines[lineno] = lines[lineno].replace(t, '')
        x = re.match(r'[ ]*def[ ]+[A-Za-z0-9_]+ \(',
                     lines[lineno])
        if x:
            lines[lineno] = lines[lineno].replace(' (', '(')
        x = re.match(r'[ ]*class[ ]+[A-Za-z0-9_]+ \(',
                     lines[lineno])
        if x:
            lines[lineno] = lines[lineno].replace(' (', '(')
        x = re.match(
            r'class[ ]+[A-Za-z0-9_]+[ ]*\(.*pyxb.binding.datatypes.decimal',
            lines[lineno])
        if x:
            lines[lineno] = lines[lineno].replace('datatypes.decimal',
                                                  'datatypes.string')
        x = re.match(
            '[ ]*[^#].*pyxb.binding.datatypes.decimal',
            lines[lineno])
        if x:
            i = lines[lineno].find('=')
            token = lines[lineno][0:i].rstrip()
            lines[lineno] = '# ' + lines[lineno]
            lines.insert(
                lineno,
                '# Follow statement ignored due conversion decimal > string')

        if len(lines[lineno]) > 80:
            ipos = 0
            x = re.match('[A-Za-z0-9_.= ]+',
                         lines[lineno][ipos:])
            if x:
                npos = ipos + x.end()
                if npos < len(lines[lineno]) and lines[lineno][npos] == '(':
                    lm = ''
                    i = 0
                    while lines[lineno][i] == ' ':
                        i += 1
                        lm += ' '
                    new_line = lm + '    ' + lines[lineno][npos + 1:]
                    lines[lineno] = lines[lineno][0:npos + 1]
                    lines.insert(lineno + 1, new_line.rstrip())
            else:
                x = re.match('[ ]*#',
                             lines[lineno][ipos:])
                if x:
                    npos = -1
                    i = 3
                    if lines[lineno].find('# Atomic simple type:') == 0:
                        rl = 25
                    else:
                        rl = min(80, len(lines[lineno]) - 75)
                    while i < rl:
                        while (i < rl and lines[lineno][i] != ' '):
                            i += 1
                        if (i < rl and lines[lineno][i] == ' '):
                            npos = i
                        i += 1
                    if npos >= 0:
                        lm = ''
                        i = 0
                        while lines[lineno][i] == ' ':
                            i += 1
                            lm += ' '
                        new_line = lm + '#' + lines[lineno][npos:]
                        lines[lineno] = lines[lineno][0:npos]
                        lines.insert(lineno + 1, new_line.rstrip())
        # ipos = 0
        # for ir in LEX_RULES.keys():
        #     x = LEX_RULES[ir].match(lines[lineno][ipos:])
        #     if x:
        #         ipos += x.end()
        lineno += 1


def main(args):
    # import pdb
    # pdb.set_trace()
    filepy = args[0][0: -3]
    FILE_SCHEMA = ''
    ix = 2
    while ix < len(args) and args[ix] == '-u':
        ix += 1
        cur_file = args[ix]
        ix += 1
        if args[ix] != '-m':
            break
        ix += 1
        cur_module = args[ix]
        ix += 1
        # SCHEMA_FILES.append(cur_file)
        # SCHEMA_FILES.append(os.path.abspath(cur_file))
        if cur_module.find(filepy) == 0:
            FILE_SCHEMA = cur_file
            break
    try:
        fd = open(args[0], 'r')
        source = fd.read()
        fd.close()
        lines = source.split('\n')
        if args[1] == '-3':
            correct_future(lines)
        else:
            robust_source(lines, FILE_SCHEMA)
            # if len(args) <= 2:
            #     wash_source(lines, '')
            # else:
            #     wash_source(lines, args[2])
            topep8(lines, FILE_SCHEMA)
        fd = open(args[0], 'w')
        fd.write(''.join('%s\n' % l for l in lines))
        fd.close()
    except BaseException:
        print "**** Error *****"


if __name__ == '__main__':
    """pyxbgeb.py filename [schema] [fmlist]
    fmlist is -u file -m module"""
    args = sys.argv[1:]
    while len(args) < 3:
        args.append('')
    main(args)
