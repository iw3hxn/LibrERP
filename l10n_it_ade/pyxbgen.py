#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyxbgen
# Agenzia delle Entrate pyxb generator
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2017 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
import sys
import os


__version__ = '0.1.5.2'


def wash_source(lines, kind):
    lineno = 0
    # TODO: patch fatturapa for OCA compatiblity, may not work in the future
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
                         lines[lineno].find(RULES_MATCH[rule])  >= 0)):
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


def robust_source(lines, model):
    RELCMNDIR = model
    ABSCMNDIR = os.path.abspath(os.getcwd() + '/' + RELCMNDIR)
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
        else:
            if lines[lineno].find(ABSCMNDIR) >= 0:
                lines[lineno] = lines[lineno].replace(ABSCMNDIR, RELCMNDIR)
        lineno += 1


def main(args):
    try:
        fd = open(args[0], 'r')
        source = fd.read()
        fd.close()
        lines = source.split('\n')
        robust_source(lines, args[1])
        wash_source(lines, args[2])
        fd = open(args[0], 'w')
        fd.write(''.join('%s\n' % l for l in lines))
        fd.close() 
    except:
        pass


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
