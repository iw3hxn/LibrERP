# -*- coding: utf-8 -*-
#
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
# Copyright 2018-19 - Odoo Community Association <https://odoo-community.org>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm


class ItalyAdeInvoiceType(orm.Model):
    _name = 'italy.ade.invoice.type'
    _description = 'Tipo Fattura Fiscale'

    _sql_constraints = [('code',
                         'unique(code)',
                         'Code already exists!')]

    _columns = {
        'code': fields.char(string='Code', size=4,
                           help='Code assigned by Tax Authority'),
        'name': fields.char(string='Name'),
        'help': fields.text(string='Help'),
        'scope': fields.char(string='Scope',
                            help='Reserved to specific scope'),
        'active': fields.boolean(string='Active',
                                default=True),
    }
