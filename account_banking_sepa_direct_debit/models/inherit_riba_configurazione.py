# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class riba_configurazione(orm.Model):

    _inherit = 'riba.configurazione'

    _columns = {
        'sdd': fields.boolean('SDD'),
        'PrvtId': fields.char('Identificativo creditore', help='Client ID fornito dalla propria banca'),
        'cuc': fields.char('CUC creditore', size=8, help='Codice Univoco CBI fornito dalla propria banca'),
        'sdd_type': fields.selection((('CORE', 'Core'), ('B2B', 'B2B')), 'Direct debit type'),
    }

    _defaults = {
        'sdd': False,
        'sdd_type': 'CORE'
    }
