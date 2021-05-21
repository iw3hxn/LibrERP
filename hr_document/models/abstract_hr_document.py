# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Dhaval Patel (dhpatel82 at gmail.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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
import datetime

from openerp.addons import base
from openerp.osv import orm, fields


class HrDocumentAbstract(orm.AbstractModel):
    _description = "HR Employee Document"
    _name = 'hr.document.abstract'

    def _get_document_years(self, cr, uid, fields, context=None):
        result = []
        first_document_ids = self.search(cr, uid, [('valid_start_date', '!=', False)], order='date asc', limit=1, context=context)
        if first_document_ids:
            first_document = self.browse(cr, uid, first_document_ids[0], context)
            first_year = datetime.datetime.strptime(first_document.valid_start_date, '%Y-%m-%d').year
        else:
            first_year = datetime.date.today().year

        for year in range(int(first_year), int(datetime.date.today().year) + 1):
            result.append((str(year), str(year)))

        return result

    def _get_document_year(self, cr, uid, ids, field_name, arg, context):

        result = {}
        for document in self.browse(cr, uid, ids, context):
            if document.valid_start_date:
                result[document.id] = datetime.datetime.strptime(document.valid_start_date, '%Y-%m-%d').year
            else:
                result[document.id] = False

        return result

    _columns = {
        'year': fields.function(_get_document_year, 'Year', type='selection', selection=_get_document_years,
                                method=True, help="Select year"),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'name': fields.char("Document", size=256, required=True),
        'document_type_id': fields.many2one('hr.document.type', 'Document Type'),
        'valid_start_date': fields.date("Valid Start Date"),
        'valid_end_date': fields.date("Valid End Date"),
        'planned_date': fields.date("Planned Date"),
        'comments': fields.text('Comments'),
        'has_date_option': fields.boolean('Has date options ?'),
        'active': fields.boolean('Active'),
        'ref_type': fields.char("Reference Type"),
        'ref': fields.reference('Reference', selection=base.res.res_request._links_get, size=None),
    }
    _defaults = {
        'active': 1,
    }
    _order = "document_type_id desc"

    def _check_dates(self, cr, uid, ids, context=None):
        for i in self.browse(cr, uid, ids, context=context):
            if i.has_date_option and i.valid_start_date >= i.valid_end_date:
                return False
        return True

    _constraints = [(_check_dates, 'Error! Documents start date must be lower then contract end date.',
                     ['has_date_option', 'valid_start_date', 'valid_end_date'])]

    def onchange_document_type_id(self, cr, uid, ids, document_type_id, context=None):
        has_date_option = False
        if document_type_id:
            document_type_obj = self.pool['hr.document.type']
            document_type = document_type_obj.browse(cr, uid, [document_type_id], context)
            has_date_option = True if document_type and document_type[0].has_date_option else False
        return {'value': {'has_date_option': has_date_option}}
