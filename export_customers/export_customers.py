# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import base64
from osv import fields, osv


class export_customers(osv.osv_memory):
    """
    Wizard to Exporting customers in .csv file for italian fiscal program.
    """
    _name = "export.customers"
    _description = "Export Customers"

    _columns = {
        'filename': fields.char('Filename', 32, required=True),
        'name': fields.char('name', 32),
        'data': fields.binary('File', readonly=True),
    }
    _defaults = {
        'filename': 'clienti',
    }

    def unicode2ascii(self, text):
        text = text.replace("è", "e'")
        text = text.replace("ò", "o'") 
        text = text.replace("à", "a'") 
        text = text.replace("ì", "i'") 
        text = text.replace("é", "e'") 
        text = text.replace("ù", "u'") 
        return text
    
    def exporting_customers(self, cr, uid, ids, context={}):
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        account_obj = self.pool.get('account.account')
        payment_term_obj = self.pool.get('account.payment.term')
        province_obj = self.pool.get('res.province')
        control_vat = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

        this = self.browse(cr, uid, ids)[0]

        name = this.filename
        filename_len = len(name)
        
        output = "1; vat ; fcode ; customer_ledger_code ; customer_code ; 1 ;partner_name_1  ;  partner_name_2 ; street[:34] ; zip ; city ;  province_abbreviation ; country_name ; phone ; ; fax ; email ; customer_ref ; account_position ; payment_term \n"
        
        extension = name[filename_len - 4:filename_len]
        if extension != '.csv':
            name = name + '.csv'

        
        partner_ids = partner_obj.search(cr, uid, [('customer', '=', True)])
        partner_datas = partner_obj.read(cr, uid, partner_ids, ['vat', 'fiscalcode', 'property_account_receivable', 'name', 'address', 'property_customer_ref', 'property_account_position', 'property_payment_term', 'vat_subjected'], context=context)

        for partner_data in partner_datas:
            if partner_data['vat']:
                vat = partner_data['vat'].encode('utf-8', 'ignore')
                if vat[:1] in control_vat:
                    vat = vat[2:]
            else:
                vat = ''

            if partner_data['fiscalcode']:
                fcode = partner_data['fiscalcode'].encode('utf-8', 'ignore')
            else:
                fcode = ''

            account_data = account_obj.read(cr, uid, partner_data['property_account_receivable'][0], ['code', 'parent_id'], context=context)
            customer_ledger_code = account_data['code'].encode('utf-8', 'ignore')

            code_account = ''
            if account_data['parent_id']:
                code_account_data = account_obj.read(cr, uid, account_data['parent_id'][0], ['code'], context=context)
                code_account = code_account_data['code'].encode('utf-8', 'ignore')
            
            partner_name = partner_data['name'].encode('utf-8', 'ignore')
            len_partner_name = len(partner_name)
            if len_partner_name > 60:
                partner_name_1 = partner_name[0: 29]
                partner_name_2 = partner_name[29: 59]
            elif len_partner_name > 30:
                partner_name_1 = partner_name[0: 29]
                partner_name_2 = partner_name[29: len_partner_name]
            else:
                partner_name_1 = partner_name
                partner_name_2 = ""

            find = False
            street = ''
            zip = ''
            city = ''
            phone = ''
            fax = ''
            email = ''
            province_id = False
            country_id = False
            address_datas = address_obj.read(cr, uid, partner_data['address'], ['type', 'street', 'street2', 'zip', 'city', 'province', 'phone', 'fax', 'email', 'country_id'], context=context)
            for address_data in address_datas:
                if address_data['type'] == 'invoice':
                    if address_data['street']:
                        street = address_data['street'].encode('utf-8', 'ignore')
                    if address_data['street2']:
                        if not street:
                            street = address_data['street2'].encode('utf-8', 'ignore')
                        else:
                            street = street + ' - ' + address_data['street2'].encode('utf-8', 'ignore')
                    if address_data['zip']:
                        zip = address_data['zip'].encode('utf-8', 'ignore')
                    if address_data['city']:
                        city = address_data['city'].encode('utf-8', 'ignore')
                    if address_data['province']:
                        province_id = address_data['province'][0]
                    if address_data['phone']:
                        phone = address_data['phone'].encode('utf-8', 'ignore')
                    if address_data['fax']:
                        fax = address_data['fax'].encode('utf-8', 'ignore')
                    if address_data['email']:
                        email = address_data['email'].encode('utf-8', 'ignore')
                    if address_data['country_id']:
                        country_id = address_data['country_id'][0]
                    find = True
                    break
            if not find:
                for address_data in address_datas:
                    if address_data['type'] == 'default':
                        street = ''
                        if address_data['street']:
                            street = address_data['street'].encode('utf-8', 'ignore')
                        if address_data['street2']:
                            if not street:
                                street = address_data['street2'].encode('utf-8', 'ignore')
                            else:
                                street = street + ' - ' + address_data['street2'].encode('utf-8', 'ignore')
                        if address_data['zip']:
                            zip = address_data['zip'].encode('utf-8', 'ignore')
                        if address_data['city']:
                            city = address_data['city'].encode('utf-8', 'ignore')
                        if address_data['province']:
                            province_id = address_data['province'][0]
                        if address_data['phone']:
                            phone = address_data['phone'].encode('utf-8', 'ignore')
                        if address_data['fax']:
                            fax = address_data['fax'].encode('utf-8', 'ignore')
                        if address_data['email']:
                            email = address_data['email'].encode('utf-8', 'ignore')
                        if address_data['country_id']:
                            country_id = address_data['country_id'][0]
                            
                        find = True
                        break
            if not find:
                for address_data in address_datas:
                    if not address_data['type']:
                        street = ''
                        if address_data['street']:
                            street = address_data['street'].encode('utf-8', 'ignore')
                        if address_data['street2']:
                            if not street:
                                street = address_data['street2'].encode('utf-8', 'ignore')
                            else:
                                street = street + ' - ' + address_data['street2'].encode('utf-8', 'ignore')
                        if address_data['zip']:
                            zip = address_data['zip'].encode('utf-8', 'ignore')
                        if address_data['city']:
                            city = address_data['city'].encode('utf-8', 'ignore')
                        if address_data['province']:
                            province_id = address_data['province'][0]
                        if address_data['phone']:
                            phone = address_data['phone'].encode('utf-8', 'ignore')
                        if address_data['fax']:
                            fax = address_data['fax'].encode('utf-8', 'ignore')
                        if address_data['email']:
                            email = address_data['email'].encode('utf-8', 'ignore')
                        if address_data['country_id']:
                            country_id = address_data['country_id'][0]
                        find = True
                        break
            
            if country_id:
                country = self.pool.get('res.country').browse(cr, uid, country_id)
                country_name = country.name.encode('utf-8', 'ignore')
            else:
                country_name = ''
                
        
            province_abbreviation = ''
            if province_id:
                province_data = province_obj.read(cr, uid, province_id, ['code'], context=context)
                province_abbreviation = province_data['code'].encode('utf-8', 'ignore')

            if ('property_customer_ref' in partner_data) and partner_data['property_customer_ref']:
                customer_ref = partner_data['property_customer_ref'].encode('utf-8', 'ignore')
                customer_code = partner_data['property_customer_ref'].encode('utf-8', 'ignore')
            else:
                customer_ref = partner_name_1
                customer_code = ''
            
            account_position = ''
            if partner_data['property_account_position']:
                account_position = str(partner_data['property_account_position'][1])

            payment_term = ''
            if partner_data['property_payment_term']:
                payment_term_data = payment_term_obj.read(cr, uid, partner_data['property_payment_term'][0], ['name'], context=context)
                payment_term = str(payment_term_data['name'])
                
            output += "1;" + vat + ";" + fcode + ";" + customer_ledger_code + ";" + customer_code + ";1;" + partner_name_1 + ";" + partner_name_2 + ";" + street[:34] + ";" + zip + ";" + city + ";" + province_abbreviation + ";" + country_name + ";" + phone + ";;" + fax + ";" + email + ";" + customer_ref + ";" + account_position + ";" + payment_term + "\n"
        output = self.unicode2ascii(output)
        out = base64.encodestring(output)
        return self.write(cr, uid, ids, {'data': out, 'name': name}, context=context)

export_customers()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
