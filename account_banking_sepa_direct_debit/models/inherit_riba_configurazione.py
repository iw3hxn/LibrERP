# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class riba_configurazione(orm.Model):

    _inherit = 'riba.configurazione'

    _columns = {
        'sdd': fields.boolean('SDD'),
        'PrvtId': fields.char('Identificativo creditore')
    }

    _defaults = {
        'sdd': False,
    }
