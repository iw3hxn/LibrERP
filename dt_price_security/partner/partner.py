# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import orm
from lxml import etree

class res_partner(orm.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        group_obj = self.pool['res.groups']
        ret = super(res_partner, self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context,
                                                       toolbar=toolbar, submenu=submenu)
        
        if group_obj.user_in_group(cr, user, user, 'dt_price_security.hide_purchase_prices', context=context):
            if 'arch' in ret:
                xml = ret['arch']
                root = etree.XML(xml)
                
                to_remove = root.xpath('//form//field[@name="property_product_pricelist_purchase"]')
                if to_remove:
                    if isinstance(to_remove, list):
                        to_remove = to_remove[0]
                    group_to_remove = to_remove.getparent()
                    group_to_remove.getparent().remove(group_to_remove)
                
                ret['arch'] = etree.tostring(root)
        return ret
