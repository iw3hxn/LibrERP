# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from openerp import pooler
import logging

logger = logging.getLogger(__name__)


class res_company(orm.Model):
    _inherit = 'res.company'

    def _get_country(self, cr, uid, company_id, context=None):
        """Some fields are country dependent"""
        country_id = False
        country_code = False
        assert isinstance(company_id, int), 'Only one company ID'
        company = self.browse(cr, uid, company_id, context)
        if company.country_id:
            country_code = company.country_id.code
        elif company.vat:
            country_code = company.vat[0:2].upper()
            ids = pooler.get_pool(cr.dbname).\
                get('res.country').search(cr, uid,
                                          [('code', '=', country_code)])
            if ids:
                country_id = ids[0]
        return country_id, country_code