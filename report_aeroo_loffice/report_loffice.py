# -*- coding: utf-8 -*-
# © 2018 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import netsvc
from DocumentConverter import DocumentConverter
from report.report_sxw import rml_parse
import logging
_logger = logging.getLogger(__name__)


class OpenOffice_service(DocumentConverter, netsvc.Service):
    def __init__(self, cr, cmd=False, dir_tmp=False):
        if not cmd or not dir_tmp:
            cr.execute("SELECT soffice, dir_tmp FROM oo_config")
            cmd, dir_tmp = cr.fetchone()
        # cmd = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        DocumentConverter.__init__(self, cmd, prefix='aeroo-', dir_tmp=dir_tmp, suffix='.odt')
        netsvc.Service.__init__(self, 'openoffice')


class oo_config(orm.Model):
    '''
        LibreOffice connection
    '''
    _name = 'oo.config'
    _description = 'LibreOffice connection'

    _columns = {
        'soffice': fields.char('Path to LibreOffice executable', size=256, required=True),
        'dir_tmp': fields.char('Temp directory', size=256, required=True)
    }

    _default = {
        'dir_tmp': '/tmp'
    }


class report_xml(orm.Model):
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'process_sep': fields.boolean('Process Separately')
    }

    def register_all(self, cr):
        super(report_xml, self).register_all(cr)
        ########### Run OpenOffice service ###########

        cr.execute("SELECT id, state FROM ir_module_module WHERE name='report_aeroo_loffice'")
        helper_module = cr.dictfetchone()
        helper_installed = helper_module['state'] == 'installed'

        if OpenOffice_service and helper_installed:
            try:
                OpenOffice_service(cr)
                _logger.info("LibreOffice.org connection successfully established")
            except Exception, e:
                cr.rollback()
                _logger.error(str(e))
        ##############################################

        cr.execute(
            "SELECT * FROM ir_act_report_xml WHERE report_type = 'aeroo' and active = true ORDER BY id")  # change for OpenERP 6.0
        records = cr.dictfetchall()
        for record in records:
            parser = rml_parse
            if record['parser_state'] == 'loc' and record['parser_loc']:
                parser = self.load_from_file(record['parser_loc'], cr.dbname, record['id']) or parser
            elif record['parser_state'] == 'def' and record['parser_def']:
                parser = self.load_from_source("from report import report_sxw\n" + record['parser_def']) or parser
            self.register_report(cr, record['report_name'], record['model'], record['report_rml'], parser)
