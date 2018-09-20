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
from openerp.osv import orm, fields
from . import res_car
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class res_car_document_type(orm.Model):
    _description = "Documents Types"
    _name = 'res.car.document.type'
    _columns = {
        'name': fields.char("Document Type", size=256, required=True),
        'code': fields.char("Code", size=64),
        'has_date_option': fields.boolean('Has date options ?'),
        'duration': fields.integer("Month Duration"),
        'repeatable': fields.boolean('Repeatable?'),
    }
    _order = "name"

    _defaults = {
        'duration': '0',
    }


class res_car_document(orm.Model):
    _description = "Car Document"
    _name = 'res.car.document'

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        for document in self.read(cr, uid, ids, context):
            if document['active']:
                if document['valid_end_date'] and (document['valid_end_date'] <= today):
                    color = 'red'
                else:
                    color = 'black'
            else:
                color = 'grey'
            value[document['id']] = color
        return value

    _columns = {
        'name': fields.char("Document", size=256, required=True),
        'document_type_id': fields.many2one('res.car.document.type', 'Document Type'),
        'car_id': fields.many2one('res.car', 'Car', ondelete='cascade', required=True),
        'valid_start_date': fields.date("Valid Start Date"),
        'valid_end_date': fields.date("Valid End Date"),
        'comments': fields.text('Comments'),
        'has_date_option': fields.boolean('Has date options ?'),
        'active': fields.boolean('Active'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True, )
    }
    _defaults = {
        'active': 1,
    }

    _order = "name"

    def _check_dates(self, cr, uid, ids, context=None):
        for document in self.browse(cr, uid, ids, context=context):
            if document.has_date_option and document.valid_start_date >= document.valid_end_date:
                return False
        return True

    _constraints = [(_check_dates, 'Error! Documents start date must be lower then contract end date.',
                     ['has_date_option', 'valid_start_date', 'valid_end_date'])]

    def onchange_document_type_id(self, cr, uid, ids, document_type_id, context=None):
        has_date_option = False
        if document_type_id:
            document_type_obj = self.pool['res.car.document.type']
            document_type = document_type_obj.browse(cr, uid, [document_type_id], context)
            if document_type and document_type[0].has_date_option:
                has_date_option = True
        return {'value': {'has_date_option': has_date_option}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
