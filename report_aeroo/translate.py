# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (c) 2009-2011 Alistek Ltd (http://www.alistek.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import netsvc
import os
import logging
import pooler
import re
import tools
from tools.translate import trans_parse_rml, trans_parse_xsl, trans_parse_view
import itertools
import fnmatch
from os.path import join
from lxml import etree
from tools.misc import UpdateableStr

def extend_trans_generate(lang, modules, cr):
    logger = logging.getLogger('i18n')
    dbname = cr.dbname

    pool = pooler.get_pool(dbname)
    trans_obj = pool.get('ir.translation')
    model_data_obj = pool.get('ir.model.data')
    uid = 1
    l = pool.obj_list()
    l.sort()

    query = 'SELECT name, model, res_id, module'    \
            '  FROM ir_model_data'

    query_models = """SELECT m.id, m.model, imd.module
            FROM ir_model AS m, ir_model_data AS imd
            WHERE m.id = imd.res_id AND imd.model = 'ir.model' """

    if 'all_installed' in modules:
        query += ' WHERE module IN ( SELECT name FROM ir_module_module WHERE state = \'installed\') '
        query_models += " AND imd.module in ( SELECT name FROM ir_module_module WHERE state = 'installed') "
    query_param = None
    if 'all' not in modules:
        query += ' WHERE module IN %s'
        query_models += ' AND imd.module in %s'
        query_param = (tuple(modules),)
    query += ' ORDER BY module, model, name'
    query_models += ' ORDER BY module, model'

    cr.execute(query, query_param)

    _to_translate = []
    def push_translation(module, type, name, id, source):
        tuple = (module, source, name, id, type)
        if source and tuple not in _to_translate:
            _to_translate.append(tuple)

    def encode(s):
        if isinstance(s, unicode):
            return s.encode('utf8')
        return s

    for (xml_name,model,res_id,module) in cr.fetchall():
        module = encode(module)
        model = encode(model)
        xml_name = "%s.%s" % (module, encode(xml_name))

        if not pool.get(model):
            logger.error("Unable to find object %r", model)
            continue

        exists = pool.get(model).exists(cr, uid, res_id)
        if not exists:
            logger.warning("Unable to find object %r with id %d", model, res_id)
            continue
        obj = pool.get(model).browse(cr, uid, res_id)

        if model=='ir.ui.view':
            d = etree.XML(encode(obj.arch))
            for t in trans_parse_view(d):
                push_translation(module, 'view', encode(obj.model), 0, t)
        elif model=='ir.actions.wizard':
            service_name = 'wizard.'+encode(obj.wiz_name)
            if netsvc.Service._services.get(service_name):
                obj2 = netsvc.Service._services[service_name]
                for state_name, state_def in obj2.states.iteritems():
                    if 'result' in state_def:
                        result = state_def['result']
                        if result['type'] != 'form':
                            continue
                        name = "%s,%s" % (encode(obj.wiz_name), state_name)

                        def_params = {
                            'string': ('wizard_field', lambda s: [encode(s)]),
                            'selection': ('selection', lambda s: [encode(e[1]) for e in ((not callable(s)) and s or [])]),
                            'help': ('help', lambda s: [encode(s)]),
                        }

                        # export fields
                        if not result.has_key('fields'):
                            logger.warning("res has no fields: %r", result)
                            continue
                        for field_name, field_def in result['fields'].iteritems():
                            res_name = name + ',' + field_name

                            for fn in def_params:
                                if fn in field_def:
                                    transtype, modifier = def_params[fn]
                                    for val in modifier(field_def[fn]):
                                        push_translation(module, transtype, res_name, 0, val)

                        # export arch
                        arch = result['arch']
                        if arch and not isinstance(arch, UpdateableStr):
                            d = etree.XML(arch)
                            for t in trans_parse_view(d):
                                push_translation(module, 'wizard_view', name, 0, t)

                        # export button labels
                        for but_args in result['state']:
                            button_name = but_args[0]
                            button_label = but_args[1]
                            res_name = name + ',' + button_name
                            push_translation(module, 'wizard_button', res_name, 0, button_label)

        elif model=='ir.model.fields':
            try:
                field_name = encode(obj.name)
            except AttributeError, exc:
                logger.error("name error in %s: %s", xml_name, str(exc))
                continue
            objmodel = pool.get(obj.model)
            if not objmodel or not field_name in objmodel._columns:
                continue
            field_def = objmodel._columns[field_name]

            name = "%s,%s" % (encode(obj.model), field_name)
            push_translation(module, 'field', name, 0, encode(field_def.string))

            if field_def.help:
                push_translation(module, 'help', name, 0, encode(field_def.help))

            if field_def.translate:
                ids = objmodel.search(cr, uid, [])
                obj_values = objmodel.read(cr, uid, ids, [field_name])
                for obj_value in obj_values:
                    res_id = obj_value['id']
                    if obj.name in ('ir.model', 'ir.ui.menu'):
                        res_id = 0
                    model_data_ids = model_data_obj.search(cr, uid, [
                        ('model', '=', model),
                        ('res_id', '=', res_id),
                        ])
                    if not model_data_ids:
                        push_translation(module, 'model', name, 0, encode(obj_value[field_name]))

            if hasattr(field_def, 'selection') and isinstance(field_def.selection, (list, tuple)):
                for dummy, val in field_def.selection:
                    push_translation(module, 'selection', name, 0, encode(val))

        elif model=='ir.actions.report.xml':
            name = encode(obj.report_name)
            fname = ""
            ##### Changes for Aeroo ######
            if obj.report_type == 'aeroo':
                trans_ids = trans_obj.search(cr, uid, [('type', '=', 'report'),('res_id', '=', obj.id)])
                for t in trans_obj.read(cr, uid, trans_ids, ['name','src']):
                    push_translation(module, "report", t['name'], xml_name, t['src'])
            ##############################
            else:
                if obj.report_rml:
                    fname = obj.report_rml
                    parse_func = trans_parse_rml
                    report_type = "report"
                elif obj.report_xsl:
                    fname = obj.report_xsl
                    parse_func = trans_parse_xsl
                    report_type = "xsl"
                if fname and obj.report_type in ('pdf', 'xsl'):
                    try:
                        report_file = tools.file_open(fname)
                        try:
                            d = etree.parse(report_file)
                            for t in parse_func(d.iter()):
                                push_translation(module, report_type, name, 0, t)
                        finally:
                            report_file.close()
                    except (IOError, etree.XMLSyntaxError):
                        logger.exception("couldn't export translation for report %s %s %s", name, report_type, fname)

        for field_name,field_def in obj._table._columns.items():
            if field_def.translate:
                name = model + "," + field_name
                try:
                    trad = getattr(obj, field_name) or ''
                except:
                    trad = ''
                push_translation(module, 'model', name, xml_name, encode(trad))

        # End of data for ir.model.data query results

    cr.execute(query_models, query_param)

    def push_constraint_msg(module, term_type, model, msg):
        # Check presence of __call__ directly instead of using
        # callable() because it will be deprecated as of Python 3.0
        if not hasattr(msg, '__call__'):
            push_translation(module, term_type, model, 0, encode(msg))

    for (model_id, model, module) in cr.fetchall():
        module = encode(module)
        model = encode(model)

        model_obj = pool.get(model)

        if not model_obj:
            logging.getLogger("i18n").error("Unable to find object %r", model)
            continue

        for constraint in getattr(model_obj, '_constraints', []):
            push_constraint_msg(module, 'constraint', model, constraint[1])

        for constraint in getattr(model_obj, '_sql_constraints', []):
            push_constraint_msg(module, 'sql_constraint', model, constraint[2])

    # parse source code for _() calls
    def get_module_from_path(path, mod_paths=None):
        if not mod_paths:
            # First, construct a list of possible paths
            def_path = os.path.abspath(os.path.join(tools.config['root_path'], 'addons'))     # default addons path (base)
            ad_paths= map(lambda m: os.path.abspath(m.strip()),tools.config['addons_path'].split(','))
            mod_paths=[def_path]
            for adp in ad_paths:
                mod_paths.append(adp)
                if not os.path.isabs(adp):
                    mod_paths.append(adp)
                elif adp.startswith(def_path):
                    mod_paths.append(adp[len(def_path)+1:])
        for mp in mod_paths:
            if path.startswith(mp) and (os.path.dirname(path) != mp):
                path = path[len(mp)+1:]
                return path.split(os.path.sep)[0]
        return 'base'   # files that are not in a module are considered as being in 'base' module

    modobj = pool.get('ir.module.module')
    installed_modids = modobj.search(cr, uid, [('state', '=', 'installed')])
    installed_modules = map(lambda m: m['name'], modobj.read(cr, uid, installed_modids, ['name']))

    root_path = os.path.join(tools.config['root_path'], 'addons')

    apaths = map(os.path.abspath, map(str.strip, tools.config['addons_path'].split(',')))
    if root_path in apaths:
        path_list = apaths
    else :
        path_list = [root_path,] + apaths

    # Also scan these non-addon paths
    for bin_path in ['osv', 'report' ]:
        path_list.append(os.path.join(tools.config['root_path'], bin_path))

    logger.debug("Scanning modules at paths: ", path_list)

    mod_paths = []
    join_dquotes = re.compile(r'([^\\])"[\s\\]*"', re.DOTALL)
    join_quotes = re.compile(r'([^\\])\'[\s\\]*\'', re.DOTALL)
    re_dquotes = re.compile(r'[^a-zA-Z0-9_]_\([\s]*"(.+?)"[\s]*?\)', re.DOTALL)
    re_quotes = re.compile(r'[^a-zA-Z0-9_]_\([\s]*\'(.+?)\'[\s]*?\)', re.DOTALL)

    def export_code_terms_from_file(fname, path, root, terms_type):
        fabsolutepath = join(root, fname)
        frelativepath = fabsolutepath[len(path):]
        module = get_module_from_path(fabsolutepath, mod_paths=mod_paths)
        is_mod_installed = module in installed_modules
        if (('all' in modules) or (module in modules)) and is_mod_installed:
            logger.debug("Scanning code of %s at module: %s", frelativepath, module)
            src_file = tools.file_open(fabsolutepath, subdir='')
            try:
                code_string = src_file.read()
            finally:
                src_file.close()
            if module in installed_modules:
                frelativepath = str("addons" + frelativepath)
            ite = re_dquotes.finditer(code_string)
            code_offset = 0
            code_line = 1
            for i in ite:
                src = i.group(1)
                if src.startswith('""'):
                    assert src.endswith('""'), "Incorrect usage of _(..) function (should contain only literal strings!) in file %s near: %s" % (frelativepath, src[:30])
                    src = src[2:-2]
                else:
                    src = join_dquotes.sub(r'\1', src)
                # try to count the lines from the last pos to our place:
                code_line += code_string[code_offset:i.start(1)].count('\n')
                # now, since we did a binary read of a python source file, we
                # have to expand pythonic escapes like the interpreter does.
                src = src.decode('string_escape')
                push_translation(module, terms_type, frelativepath, code_line, encode(src))
                code_line += i.group(1).count('\n')
                code_offset = i.end() # we have counted newlines up to the match end

            ite = re_quotes.finditer(code_string)
            code_offset = 0 #reset counters
            code_line = 1
            for i in ite:
                src = i.group(1)
                if src.startswith("''"):
                    assert src.endswith("''"), "Incorrect usage of _(..) function (should contain only literal strings!) in file %s near: %s" % (frelativepath, src[:30])
                    src = src[2:-2]
                else:
                    src = join_quotes.sub(r'\1', src)
                code_line += code_string[code_offset:i.start(1)].count('\n')
                src = src.decode('string_escape')
                push_translation(module, terms_type, frelativepath, code_line, encode(src))
                code_line += i.group(1).count('\n')
                code_offset = i.end() # we have counted newlines up to the match end

    for path in path_list:
        logger.debug("Scanning files of modules at %s", path)
        for root, dummy, files in tools.osutil.walksymlinks(path):
            for fname in itertools.chain(fnmatch.filter(files, '*.py')):
                export_code_terms_from_file(fname, path, root, 'code')
            for fname in itertools.chain(fnmatch.filter(files, '*.mako')):
                export_code_terms_from_file(fname, path, root, 'report')


    out = [["module","type","name","res_id","src","value"]] # header
    _to_translate.sort()
    # translate strings marked as to be translated
    for module, source, name, id, type in _to_translate:
        trans = trans_obj._get_source(cr, uid, name, type, lang, source)
        out.append([module, type, name, id, source, encode(trans) or ''])

    return out

import sys
sys.modules['tools.translate'].trans_generate = extend_trans_generate

