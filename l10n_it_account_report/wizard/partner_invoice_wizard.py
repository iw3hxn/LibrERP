# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
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

from openerp.osv import fields, orm

class partner_invoice_wizard(orm.TransientModel):
    """
    questa classe apre il wizard per stampare il fatturato di un cliente/fornitore 
    """
    _name = 'partner.invoice.wizard'
    _description = 'Total Invoice'
    _columns = {
        'period_from_id': fields.many2one('account.period', 'Period From', required=True),
        'period_to_id': fields.many2one('account.period', 'Period To', required=True),
    }

    
    def print_report(self, cr, uid, ids, context=None):
        """
        To get the period and print the report of partner's invoice
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return : Report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['period_from_id', 'period_to_id'], context=context)
        res = res and res[0] or {}
        res['period_from_id'] = res['period_from_id'][0]
        res['period_to_id'] = res['period_to_id'][0]
        datas['form'] = res      
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'partner.total.invoice',
            'datas': datas,
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
