#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Poiesis Consulting (<http://www.poiesisconsulting.com>).
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

from osv import osv, fields

class company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'logo_web': fields.binary('Logo Header', filters='*.png,*.gif,*.jpg,*.jpeg',help="Image file for company logo at header of web client. Ideally, a 200x55 png with transparent background."),
        'color_set': fields.many2one('res.company.color', string='Color schema', help="Set of colors to display on Web client"),
        'color_top': fields.related('color_set','color_top', readonly=True, type='char'),
        'color_mid': fields.related('color_set','color_mid', readonly=True, type='char'),
        'color_low': fields.related('color_set','color_low', readonly=True, type='char'),
        'button_top': fields.related('color_set','button_top', readonly=True, type='char'),
        'button_mid': fields.related('color_set','button_mid', readonly=True, type='char'),
        'link_top': fields.related('color_set','link_top', readonly=True, type='char'),
    }

company()

class company_colors(osv.osv):
    
    _name = 'res.company.color'
    _description = 'Company color schema'
    _columns = {
        'name': fields.char('Name', size=32),
        'color_top': fields.char('Color top gradient', size=24, help="Hexagesimal color code for the upper end of color gradient"),
        'color_mid': fields.char('Color main gradient', size=24, help="Hexagesimal color code for the middle color gradient"),
        'color_low': fields.char('Color low gradient', size=24, help="Hexagesimal color code for the lower end of color gradient"),
        'button_top': fields.char('Button top gradient', size=24, help="Hexagesimal color code for the upper end of button color gradient"),
        'button_mid': fields.char('Button main gradient', size=24, help="Hexagesimal color code for the middle button color gradient"),
        'link_top': fields.char('Hyperlinks color', size=24, help="Hexagesimal color code for the text of hyperlinks"),
    }
    
company_colors()
