# -*- coding: utf-8 -*-
#    Copyright (C) 2011-12 Domsense s.r.l. <http://www.domsense.com>.
#    Copyright (C) 2012-15 Agile Business Group sagl <http://www.agilebg.com>
#    Copyright (C) 2013-15 LinkIt Spa <http://http://www.linkgroup.it>
#    Copyright (C) 2013-18 Associazione Odoo Italia
#                          <http://www.odoo-italia.org>
#    Copyright (C) 2017-18 Didotech srl <http://www.didotech.com>
#    Copyright (C) 2017-18 SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'of_account_end_vat_statement_interest':
            fields.boolean('Interest on End Vat Statement',
                           help="Apply interest on end vat statement"),
        'of_account_end_vat_statement_interest_percent':
            fields.float('Interest on End Vat Statement - %',
                         help="Apply interest on end vat statement"),
        'of_account_end_vat_statement_interest_account_id':
            fields.many2one('account.account',
                            'Interest on End Vat Statement - Account',
                            help="Apply interest on end vat statement"),
    }
