# -*- coding: utf-8 -*-

#################################################################################
#    Autor: Mikel Martin (mikel@zhenit.com)
#    Copyright (C) 2012 ZhenIT Software (<http://ZhenIT.com>). All Rights Reserved
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

from openerp.osv import fields, orm
from lxml import etree


class invoice_merge(orm.TransientModel):
    """
    Merge invoices
    """

    _name = 'invoice.merge'
    _description = 'Use this wizard to merge draft invoices from the same partner'

    _columns = {
        'merge_lines': fields.boolean('Merge invoice lines',
                                      help='Merge invoice lines with same product at the same price.'),
        'invoices': fields.many2many('account.invoice', 'account_invoice_merge_rel', 'merge_id', 'invoice_id',
                                     'Invoices')
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(invoice_merge, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        parent = self.pool['account.invoice'].browse(cr, uid, context['active_id'], context)

        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='invoices']")
        for node in nodes:
            node.set('domain', '["&",("partner_id", "=", ' + str(parent.partner_id.id) + '),("state", "=","draft")]')
        res['arch'] = etree.tostring(doc)
        context['partner'] = parent.partner_id.id
        return res

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        res = super(invoice_merge, self).default_get(cr, uid, fields, context=context)
        if context and 'active_ids' in context and context['active_ids']:
            res.update({'invoices':  context['active_ids']})

        return res

    def merge_invoices(self, cr, uid, ids, context):

        data = self.browse(cr, uid, ids, context=context)[0]
        self.pool['account.invoice'].merge_invoice(cr, uid, data.invoices, data.merge_lines, context)

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
