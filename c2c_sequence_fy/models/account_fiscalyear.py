# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp (<http://www.camptocamp.at>)
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
from osv import fields, osv


class account_fiscalyear(osv.Model):
    _inherit = "account.fiscalyear"
    _columns = {
        'sequence_code': fields.char('Sequence Code', size=6,
                                     help="""This code will be used to format the start date of the fiscalyear for the placeholder 'fy' defined for sequences as prefix and suffix.
Example: a fiscal year starting on March 1st with a sequence code %Ya will generate 2011a.
This allows to handle multiple fiscal years per calendar year and fiscal years not matching calendar years easily""")
    }
