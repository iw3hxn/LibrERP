# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Didotech SRL
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
import logging
import addons


class res_partner(osv.osv):

    _inherit = "res.partner"
    _columns = {
        'partner_logo': fields.binary('Photo'),
    }

    def _get_photo(self, cr, uid, context=None):
        photo_path = addons.get_module_resource('partner_kanban', 'images', 'photo.png')
        return open(photo_path, 'rb').read().encode('base64')

    _defaults = {
        'partner_logo': _get_photo,
    }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
