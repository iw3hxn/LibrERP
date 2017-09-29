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


__version__ = '0.1.5.1'


def wash_source(lines, kind):
    lineno = 0
    # TODO: patch fatturapa for OCA compatiblity, may not work in the future
    patch = 0
    while lineno < len(lines):
        if not lines[lineno] or not kind:
            pass
        elif lines[lineno].startswith('class RateType'):
            lines[lineno] = lines[lineno].replace('.decimal)', '.string)')
            patch = 1
        elif lines[lineno].startswith('class PesoType') or \
                lines[lineno].startswith('class Amount8DecimalType') or \
                lines[lineno].startswith('class Amount2DecimalType') or \
                lines[lineno].startswith('class RateType') or \
                lines[lineno].startswith('class QuantitaType'):
            lines[lineno] = lines[lineno].replace('.decimal)', '.string)')
            patch = 0
        elif lines[lineno].startswith('class '):
            patch = 0
        elif lines[lineno].startswith('RateType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive') or \
                lines[lineno].find("value_datatype=RateType, value=pyxb.binding.datatypes.decimal('100.0')") >=0 or \
                lines[lineno].find('RateType._CF_maxInclusive') >= 0:
            if patch:
                lines[lineno] = '# ' + lines[lineno]
        elif lines[lineno] == 'RateType._InitializeFacetMap(RateType._CF_pattern,':
            if patch:
                lines[lineno] = lines[lineno][0:-1] + ')'
        lineno += 1


def main(args):
    try:
        fd = open(args[0], 'r')
        source = fd.read()
        fd.close()
        lines = source.split('\n')
        saved_lines = []
        state = 0
        lineno = 0
        RELCMNDIR = args[1]
        ABSCMNDIR = os.path.abspath(os.getcwd() + '/' + RELCMNDIR)
        lines.insert(lineno,
                     '# flake8: noqa')
        lineno += 1
        lines.insert(lineno,
                     '# -*- coding: utf-8 -*-')
        lineno += 1
        while lineno < len(lines):
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
                elif lines[lineno][0:10] == 'import _cm' or \
                        lines[lineno][0:10] == 'import _ds':
                    lines[lineno] = 'from . %s' % lines[lineno]
            elif state == 1:
                # lines.insert(lineno,
                #              '# from openerp import addons')
                # lineno += 1
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
                # lines.insert(lineno,
                #              '# common = addons.get_module_resource(\'l10n_it_fatturapa\')')
                # lineno += 1
                # lines.insert(lineno,
                #              '# if not common:')
                # lineno += 1
                # lines.insert(lineno,
                #              '# common = \'../data/common\'')
                # lineno += 1
                lines.insert(lineno,
                             '')
                lineno += 1
                state = 2
            else:
                if lines[lineno].find(ABSCMNDIR) >= 0:
                    lines[lineno] = lines[lineno].replace(ABSCMNDIR, RELCMNDIR)
            lineno += 1
        wash_source(lines, args[2])
        fd = open(args[0], 'w')
        fd.write(''.join('%s\n' % l for l in lines))
        fd.close() 
    except:
        pass


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
