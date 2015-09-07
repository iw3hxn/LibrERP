
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


#
### HEREDO LA CLASE PRODUCTO PARA RELACIONARLA CON PROYECTOS
#
class product_product(orm.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    #
    ### SI CAMBIAN LA CATEGORIA DEL PRODUCTO
    #
    def onchange_categ_id(self, cr, uid, ids, field, categ_id, purchase_ok=None, type='consu', is_kit=None, context=None):
        """
        When category changes, we search for taxes, UOM and product type
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid, context=context)

        res = {}
        warn = False
        if ids:
            product = self.browse(cr, uid, ids, context)[0]
        else:
            product = False

        if field == 'purchase_ok' and product and type != 'service' and not purchase_ok and not is_kit:
            warn = {
                    'title': _('Error'),
                    'message': _("For change you need to create BOM"),
            }
            res['purchase_ok'] = product.purchase_ok
            return {'value': res, 'warning': warn}
        if field == 'supply_method' and product and type != 'service':
            warn = {
                    'title': _('Error'),
                    'message': _("For change you need to create BOM"),
            }
            res['supply_method'] = product.supply_method
            return {'value': res, 'warning': warn}

        if not categ_id:
            res = {
                'categ_id': False,
                'uom_id': False,
                'uom_po_id': False,
                'taxes_id': [],
                'supplier_taxes_id': [],
            }
        else:
            # Search for the default value on this category
            category_data = self.pool['product.category'].browse(cr, uid, categ_id, context=context)
            message = []
            if category_data.property_account_expense_categ:
                res['property_account_expense'] = category_data.property_account_expense_categ.id
                if product and product.property_account_expense.id != res['property_account_expense']:
                    message.append(self.fields_get(cr, uid)['property_account_expense']['string'])

            if category_data.property_account_income_categ:
                res['property_account_income'] = category_data.property_account_income_categ.id
                if product and product.property_account_income.id != res['property_account_income']:
                    message.append(self.fields_get(cr, uid)['property_account_income']['string'])

            if category_data.provision_type:
                res['type'] = category_data.provision_type
            else:
                res['type'] = type
            if product and product.type != res['type']:
                    message.append(self.fields_get(cr, uid)['type']['string'])

            if category_data.procure_method:
                res['procure_method'] = category_data.procure_method
            if category_data['supply_method']:
                res['supply_method'] = category_data.supply_method
                
            if res['type'] == 'service':
                if purchase_ok:
                    res['supply_method'] = 'buy'
                else:
                    res['supply_method'] = 'produce'
            else:
                if is_kit:
                    res['supply_method'] = 'produce'
                    res['purchase_ok'] = False
                else:
                    res['supply_method'] = 'buy'
                    res['purchase_ok'] = True
                    
            if category_data.sale_taxes_ids:
                taxes = [x.id for x in category_data.sale_taxes_ids]
                res['taxes_id'] = [(6, 0, [taxes])]

            if category_data.purchase_taxes_ids:
                taxes = [x.id for x in category_data.purchase_taxes_ids]
                res['supplier_taxes_id'] = [(6, 0, [taxes])]

            if category_data.uom_id:
                res['uom_id'] = category_data.uom_id.id
                if product and product.uom_id.id != res['uom_id']:
                    message.append(self.fields_get(cr, uid)['uom_id']['string'])

            if category_data.uom_po_id:
                res['uom_po_id'] = category_data.uom_po_id.id
                if product and product.uom_po_id.id != res['uom_po_id']:
                    message.append(self.fields_get(cr, uid)['uom_po_id']['string'])

            if category_data.uos_id:
                res['uos_id'] = category_data.uos_id.id
                res['uos_coef'] = category_data.uos_coef
                if product and product.uos_id.id != res['uos_id']:
                    message.append(self.fields_get(cr, uid)['uos_id']['string'])
                if product and product.uos_coef.id != res['uos_coef']:
                    message.append(self.fields_get(cr, uid)['uos_coef']['string'])

            if len(ids) == 1 and message and field == 'categ_id':
                warn = {
                    'title': _('Caution'),
                    'message': _("The product category has changed, thanks to control : \n %s " % '\n'.join(message)),
                }

        return {'value': res, 'warning': warn}