# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#    © 2017-2019 Didotech srl (www.didotech.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _

SOCIAL_SECURITY_TYPE = [
    ('TC01', 'Cassa Nazionale Previdenza e Assistenza Avvocati e Procuratori Legali'),
    ('TC02', 'Cassa Previdenza Dottori Commercialisti'),
    ('TC03', 'Cassa Previdenza e Assistenza Geometri'),
    ('TC04', 'Cassa Nazionale Previdenza e Assistenza Ingegneri e Architetti Liberi Professionisti'),
    ('TC05', 'Cassa Nazionale del Notariato'),
    ('TC06', 'Cassa Nazionale Previdenza e Assistenza Ragionieri e Periti Commerciali'),
    ('TC07', 'Ente Nazionale Assistenza Agenti e Rappresentanti di Commercio (ENASARCO)'),
    ('TC08', 'Ente Nazionale Previdenza e Assistenza Consulenti del Lavoro (ENPACL)'),
    ('TC09', 'Ente Nazionale Previdenza e Assistenza Medici (ENPAM)'),
    ('TC10', 'Ente Nazionale Previdenza e Assistenza Farmacisti (ENPAF)'),
    ('TC11', 'Ente Nazionale Previdenza e Assistenza Veterinari (ENPAV)'),
    ('TC12', "Ente Nazionale Previdenza e Assistenza Impiegati dell'Agricoltura (ENPAIA)"),
    ('TC13', "Fondo Previdenza Impiegati Imprese di Spedizione e Agenzie Marittime"),
    ('TC14', 'Istituto Nazionale Previdenza Giornalisti Italiani (INPGI)'),
    ('TC15', 'Opera Nazionale Assistenza Orfani Sanitari Italiani (ONAOSI)'),
    ('TC16', 'Cassa Autonoma Assistenza Integrativa Giornalisti Italiani (CASAGIT)'),
    ('TC17', 'Ente Previdenza Periti Industriali e Periti Industriali Laureati (EPPI)'),
    ('TC18', 'Ente Previdenza e Assistenza Pluricategoriale (EPAP)'),
    ('TC19', 'Ente Nazionale Previdenza e Assistenza Biologi (ENPAB)'),
    ('TC20', 'Ente Nazionale Previdenza e Assistenza Professione Infermieristica (ENPAPI)'),
    ('TC21', 'Ente Nazionale Previdenza e Assistenza Psicologi (ENPAP)'),
    ('TC22', 'INPS')
]


class AccountTax(orm.Model):
    _inherit = 'account.tax'

    def _non_taxable_nature(self, cr, uid, context=None):
        return self.pool['italy.ade.tax.nature'].get_non_taxable_nature(cr, uid, context=context)

    def _payment_reason(self, cr, uid, context=None):
        return self.pool['italy.ade.payment.reason'].get_payment_reason(cr, uid, context=context)

    _columns = {
        'non_taxable_nature': fields.selection(_non_taxable_nature, string="Non taxable nature"),
        'payability': fields.selection([
            ('I', 'Immediate payability'),
            ('D', 'Deferred payability'),
            ('S', 'Split payment'),
            ], string="VAT payability"),
        'law_reference': fields.char(
            'Law reference', size=100),
        'withholding_tax': fields.boolean("Ritenuta d'acconto"),
        'causale_pagamento_id': fields.selection(_payment_reason, string="Causale Ritenuta"),
        'withholding_type_id': fields.many2one('italy.ade.withholding.type', string='Tipo Ritenuta'),
        'social_security': fields.boolean("Cassa Previdenziale"),
        'social_security_type': fields.selection(SOCIAL_SECURITY_TYPE, string='Tipo Cassa Previdenziale'),
        'amount_e_invoice': fields.integer(
            'Amount in XML', required=False,
            help="For taxes of type percentage, enter % ratio between 0-100"),
    }
    _sql_constraints = [
        ('description_uniq', 'unique(description)', _('Description must be unique !')),
    ]
    # _defaults = {
    #     'payability': 'I',
    # }

    def copy(self, cr, uid, ids, defaults, context=None):
        defaults.update({
            'description': False
        })
        return super(AccountTax, self).copy(cr, uid, ids, defaults, context)

    def get_tax_by_invoice_tax(self, cr, uid, invoice_tax, context=None):
        if ' - ' in invoice_tax:
            tax_descr = invoice_tax.split(' - ')[0]
            tax_ids = self.search(cr, uid, [
                ('description', '=', tax_descr),
                ], context=context)
            if not tax_ids:
                raise orm.except_orm(
                    _('Error'), _('No tax %s found') %
                    tax_descr)
            if len(tax_ids) > 1:
                raise orm.except_orm(
                    _('Error'), _('Too many tax %s found') %
                    tax_descr)
        else:
            tax_name = invoice_tax
            tax_ids = self.search(cr, uid, [
                ('name', '=', tax_name),
                ], context=context)
            if not tax_ids:
                raise orm.except_orm(
                    _('Error'), _('No tax %s found') %
                    tax_name)
            if len(tax_ids) > 1:
                raise orm.except_orm(
                    _('Error'), _('Too many tax %s found') %
                    tax_name)
        return tax_ids[0]
