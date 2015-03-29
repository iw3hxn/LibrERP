
##############################################################################
#
#    Author: Didotech SRL
#    Copyright 2014 Didotech SRL
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

from openerp.osv import orm, fields


class res_company(orm.Model):

    _inherit = 'res.company'

    def _getFiscalPosition(self, cr, uid, context=None):
        fiscal_position_obj = self.pool['account.fiscal.position']
        fiscal_position_ids = fiscal_position_obj.serach(cr, uid, [], context=context)
        if fiscal_position_ids:
            return fiscal_position_ids[0]
        else:
            return False

    _columns = {
        'check_credit_limit': fields.boolean('Abilita gestione fido'),
        'default_credit_limit': fields.float(string='Fido di default'),
        'enable_margin_validation': fields.boolean('Enable Margin Verify'),
        'minimum_margin': fields.float(string='Minimun margin %', digits=(2, 2)),
        'default_sale_order_validity': fields.integer('Default day of validity'),
        'default_property_account_position': fields.property(
            'account.fiscal.position',
            type='many2one',
            relation='account.fiscal.position',
            string="Default Fiscal Position",
            view_load=True,
            help="The default fiscal position will determine taxes and the accounts used for the partner.",
        ),
        'default_property_payment_term': fields.property(
            'account.payment.term',
            type='many2one',
            relation='account.payment.term',
            string ='Default Payment Term',
            view_load=True,
            help="This default payment term will be used on creation of partner"),
        'need_tech_validation': fields.boolean('Need Technical Verification'),
        'need_manager_validation': fields.boolean('Need Supervisor Verification'),
        'readonly_price_unit': fields.boolean('Read Only Price Unit on Sale Order'),
    }

    _defaults = {
        'check_credit_limit': True,
        'need_tech_validation': False,
        'need_manager_validation': False,
        'default_credit_limit': 0,
        'default_sale_order_validity': 30,
        'default_property_account_position': _getFiscalPosition,
    }
