# -*- coding: utf-8 -*-
#
# Copyright 2020 - Didotech s.r.l. <https://www.didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm


class ItalyAdePaymentReason(orm.Model):
    _name = 'italy.ade.payment.reason'
    _description = 'Italian Official Payment Reason'

    _columns = {
        'code': fields.char(string='Code', size=4),
        'name': fields.char(string='Description'),
        'active': fields.boolean(string='Active', default=True)
    }
    _order = 'code'

    _sql_constraints = [
        ('code', 'unique(code)', 'Code already exists!')
    ]

    def get_payment_reason(self, cr, uid, context=None):
        reason_ids = self.search(cr, uid, [('active', '=', True)], context=context)
        return [
            (reason.code, reason.name)
            for reason in self.browse(cr, uid, reason_ids, context=context)
        ]
