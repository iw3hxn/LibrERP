# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2025 Didotech SRL
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

SUPPLIER_TYPE_SELECTION = [
    ('QC_important', 'QC Importante'),
    ('QC_primary', 'QC Primario'),
    ('QC_secondary', 'QC Secondario'),
]


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'supplier_type': fields.selection(
            SUPPLIER_TYPE_SELECTION,
            'Classificazione QC fornitore',
            help="Classificazione qualita' del fornitore ai fini ISO 9001: "
                 "determina quali fornitori compaiono di default nel report "
                 "ritardi ricezione."),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
