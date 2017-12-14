# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import os
import xmltodict
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from collections import OrderedDict
from data_migration.utils.utils import Utils
import netsvc
wf_service = netsvc.LocalService("workflow")


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def load_orders(self, cr, uid, path=False, context=None):
        black_list = (
            '.DS_Store',
        )

        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        path = path or company.order_import_path

        for xml_order_file_name in os.listdir(path):
            if xml_order_file_name not in black_list:
                xml_order_file = os.path.join(path, xml_order_file_name)
                if os.path.isfile(xml_order_file):
                    with open(xml_order_file) as xml_order:
                        new_order_id = self.create_external(
                            cr, uid, xmltodict.parse(xml_order, process_namespaces=True), context)

                    processed_dir = os.path.join(path, 'processed')
                    if not os.path.isdir(processed_dir):
                        os.mkdir(processed_dir)

                    if new_order_id:
                        os.rename(xml_order_file, os.path.join(processed_dir, xml_order_file_name))
                        if company.order_import_auto_confirm:
                            wf_service.trg_validate(uid, 'sale.order', new_order_id, 'order_confirm', cr)

        return True

    def partner_from_address_data(self, cr, uid, addresses, context):
        def get_address_values(cr, uid, address_values, context):
            address_types = {
                # 'Billing': 'invoice',
                'Billing': 'default',
                'Shipping': 'delivery'
            }

            province_ids = self.pool['res.province'].search(cr, uid, [
                ('code', '=', address_values['Province'])
            ], context={'lang': 'it_IT'})

            country_ids = self.pool['res.country'].search(cr, uid, [
                ('name', '=', address_values['Country'])
            ], context={'lang': 'it_IT'})

            return {
                'type': address_types[address_values['@Type']],
                'street': address_values['Street'],
                'zip': address_values['Zip'],
                'city': address_values['City'],
                'province': province_ids and province_ids[0] or None,
                'country_id': country_ids and country_ids[0] or None,
                'active': True,
                'phone': address_values['Phone']
            }

        partner_model = self.pool['res.partner']

        if isinstance(addresses, (dict, OrderedDict)):
            addresses = [addresses]

        for address in addresses:
            partner_ids = partner_model.search(cr, uid, [
                ('external_id', '=', int(address['@UserID']))], context)
            if partner_ids:
                return partner_ids[0]
        else:
            address_values = []

            for address in addresses:
                address_values.append((0, False, get_address_values(cr, uid, address, context)))

            partner_values = {
                'name': addresses[0]['CompanyName'] or addresses[0]['Name'] + ' ' + addresses[0]['Surname'],
                'vat': addresses[0]['VatCode'],
                'address': address_values,
                'external_id': int(address['@UserID'])
            }
        return partner_model.create(cr, uid, partner_values, context)

    def order_lines_from_line_data(self, cr, uid, order_line_values, context):
        product_model = self.pool['product.product']

        order_lines = []

        if isinstance(order_line_values, (dict, OrderedDict)):
            order_line_values = [order_line_values]

        for line_values in order_line_values:
            product_id = product_model.get_create(cr, uid, line_values, context)
            product = product_model.browse(cr, uid, product_id, context)
            order_lines.append({
                'product_id': product_id,
                'name': product.name,
                'price_unit': float(Utils.toStr(line_values['Price'])),
                'product_uom_qty': float(Utils.toStr(line_values['Quantity']))
            })

        return order_lines

    def create_external(self, cr, uid, values, context=None):
        order_lines = self.order_lines_from_line_data(cr, uid, values['Order']['Items']['Item'], context)

        partner_id = self.partner_from_address_data(cr, uid, values['Order']['Address'], context)

        sale_order_values = self.onchange_partner_id(cr, uid, False, partner_id)['value']

        sale_order_values.update({
            'name': values['Order']['@Code'],
            'date_order': datetime.datetime.strptime(
                values['Order']['@Date'], DEFAULT_SERVER_DATETIME_FORMAT
            ).strftime(DEFAULT_SERVER_DATE_FORMAT),
            'partner_id': partner_id,
            'order_line': [(0, False, line) for line in order_lines]
        })

        order_ids = self.search(cr, uid, [
            ('name', '=', values['Order']['@Code'])
        ], context)

        if order_ids:
            self.write(cr, uid, order_ids, sale_order_values, context)
            return order_ids[0]
        else:
            return self.create(cr, uid, sale_order_values, context)
