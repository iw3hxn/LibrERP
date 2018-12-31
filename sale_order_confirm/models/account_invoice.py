# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-2015 Didotech srl (<http://www.didotech.com>)
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

from openerp.osv import orm, fields


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def print_report(self, cr, uid, ids, xml_id, context=None):
        def id_from_xml_id():
            report_obj = self.pool['ir.actions.report.xml']
            report_all = report_obj.search(cr, uid, [], context=context)
            report_xml_ids = report_obj.get_xml_id(cr, uid, report_all, context=context)

            for key in report_xml_ids.keys():
                xml_id_it = report_xml_ids[key]
                if xml_id_it == xml_id:
                    return key
            return False
        if not ids:
            return False

        if not isinstance(ids, list):
            ids = [ids]

        report_id = id_from_xml_id()
        report = self.pool['ir.actions.report.xml'].browse(cr, uid, report_id, context)
        data = {'model': report.model, 'ids': ids, 'id': ids[0]}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report.report_name,
            'datas': data,
            'context': context
        }

    def print_invoice(self, cr, uid, ids, context):
        return self.print_report(cr, uid, ids, 'account.account_invoices', context)

    _columns = {
        'advance_order_id': fields.many2one('sale.order', 'Order Reference', readonly=True, states={'draft': [('readonly', False)]}),
    }


