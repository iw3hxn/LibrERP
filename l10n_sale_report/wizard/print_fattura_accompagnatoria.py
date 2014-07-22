# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Associazione OpenERP Italia (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv


class wizard_fattura_accompagnatoria(osv.osv_memory):
    _name = "wizard.fattura.accompagnatoria"

    def _get_picking_ids(self, cr, uid, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = []
        if 'active_ids' in context:
            for invoice in invoice_obj.browse(cr, uid, context['active_ids'], context=context):
                for sale_order in invoice.sale_order_ids:
                    for picking in sale_order.picking_ids:
                        res.append((picking.id, picking.name))
        return res

    _columns = {
        'picking_id': fields.selection(_get_picking_ids, 'Picking', required=True),
    }

    def print_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read(cr, uid, ids)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fattura_accompagnatoria',
            'datas': datas,
        }
