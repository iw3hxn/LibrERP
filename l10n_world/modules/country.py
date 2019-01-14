# -*- coding: utf-8 -*-
# © 2019 Didotech srl (www.didotech.com)

from openerp.osv import orm

EU = [
    'BE',
    'BG',
    'CZ',
    'DK',
    'DE',
    'EE',
    'IE',
    'EL',
    'ES',
    'FR',
    'HR',
    'IT',
    'CY',
    'LV',
    'LT',
    'LU',
    'HU',
    'MT',
    'NL',
    'AT',
    'PL',
    'PT',
    'RO',
    'SI',
    'SK',
    'FI',
    'SE',
    'UK'
]


class ResCountry(orm.Model):
    _inherit = 'res.country'

    def eu_member(self, cr, uid, ids, context):
        """
        :return: True/False
        """
        if ids:
            country = self.browse(cr, uid, ids[0], context)
            return country.code in EU
        else:
            return False
