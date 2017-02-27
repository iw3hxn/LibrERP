# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""Objetos sobre las liquidación"""

from openerp.osv import orm, fields
import time


class settled_wizard(orm.TransientModel):
    """settled.wizard"""

    _name = 'settled.wizard'
    _columns = {
        'date_from': fields.date('From', required=True),
        'date_to': fields.date('To', required=True),
    }

    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def settlement_exec(self, cr, uid, ids, context=None):
        """se ejecuta correctamente desde dos."""
        for settle_period in self.browse(cr, uid, ids, context=context):
            # 'tax_id': [(6, 0, res.get('invoice_line_tax_id'))],
            pool_liq = self.pool['settlement']
            liq_id = pool_liq.search(cr, uid, [('date_to', '>=', settle_period.date_from), ('state', '!=', 'invoiced')],
                                     context=context)
            if not liq_id:
                vals = {
                    'name': settle_period.date_from + " <=> " + settle_period.date_to,
                    'date_from': settle_period.date_from,
                    'date_to': settle_period.date_to
                }
                liq_id = int(pool_liq.create(cr, uid, vals, context))
            else:
                liq_id = liq_id[0]

            pool_liq.calcula(cr, uid, liq_id, context['active_ids'], settle_period.date_from, settle_period.date_to)

        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_cancel(self, cr, uid, ids, conect=None):
        """CANCEL LIQUIDACIÓN"""
        return {
            'type': 'ir.actions.act_window_close',
        }
