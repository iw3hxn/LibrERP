# -*- encoding: utf-8 -*-
##############################################################################
#
#    Parthiv Pate, Tech Receptives, Open Source For Ideas    
#    Copyright (C) 2009-Today Tech Receptives(http://techreceptives.com).
#    All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import logging
import time

from openerp.osv import orm, fields
from tools.translate import _
from dateutil import parser

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


COLOR_SELECTION = [
    ('aqua', (u"Aqua")),
    ('black', (u"Black")),
    ('blue', (u"Blue")),
    ('brown', (u"Brown")),
    ('cadetblue', (u"Cadet Blue")),
    ('darkblue', (u"Dark Blue")),
    ('fuchsia', (u"Fuchsia")),
    ('forestgreen', (u"Forest Green")),
    ('green', (u"Green")),
    ('grey', (u"Grey")),  
    ('red', (u"Red")),
    ('orange', (u"Orange"))
]

DIRECTIONS = [
    ('in', 'IN'),
    ('out', 'OUT')
]


class res_letter(orm.Model):
    """A register class to log all movements regarding letters"""
    
    _name = 'res.letter'
    _description = "A Register class to log all movements regarding letters"
    
    def _get_number(self, cr, uid, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
            
        move = context.get('move', 'in')
        if move == 'in':
            res = self.pool['ir.sequence'].get(cr, uid, 'in.letter')
        else:
            res = self.pool['ir.sequence'].get(cr, uid, 'out.letter')
        return res
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        value = {}
        for letter in self.browse(cr, uid, ids, context):
            if letter.type:
                value[letter.id] = letter.type.color
            else:
                value[letter.id] = 'black'

        return value
    
    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        
        for letter in self.browse(cr, uid, ids, context):
            name = u'[ {type_name}: {letter_number}] {letter_name}'.format(type_name=letter.type.name,
                                                                           letter_number=letter.type.name,
                                                                           letter_name=letter.name or '')
            res.append((letter.id, name))
        return res
    
    def _get_direction(self, cr, uid, ids, field_name, arg, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for line in self.browse(cr, uid, ids, context):
            if line.type.move:
                result[line.id] = line.type.move
            else:
                result[line.id] = False
        return result
    
    def _search_direction(self, cr, uid, obj, name, args, context):
        if not args:
            return []
        
        for search in args:
            if search[0] == 'move':
                search_key = args[0][2]
                query = """SELECT res_letter.id FROM res_letter
                    LEFT JOIN letter_type 
                    ON res_letter.type = letter_type.id
                    WHERE move='{0}'""".format(search_key)
                cr.execute(query)
                letters = cr.fetchall()
                res = [letter[0] for letter in letters]
                return [('id', 'in', res)]
        return []

    def onchange_partner_id(self, cr, uid, ids, partner_id, address_id, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if partner_id:
            partner_obj = self.pool['res.partner']
            partner = partner_obj.browse(cr, uid, partner_id, context)
            address_id = partner.address and partner.address[0].id or False
        return {'value': {'address_id': address_id}}

    def _formatted_date(self, cr, uid, ids, name, args, context):
        # Italian time
        dateformat = '%d/%m/%Y'

        res = {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        for line in self.browse(cr, uid, ids, context):
            try:
                current_date = parser.parse(line.date)
                formatted_date = current_date.strftime(dateformat)
                res[line.id] = formatted_date
            except Exception as e:
                _logger.error(e.message)
                res[line.id] = '* error *'
        return res

    _columns = {
        'name': fields.char('Subject', size=128, help="Subject of letter"),
        'number': fields.char('Number', size=32, help="Autogenerated Number of letter", required=True),
        # 'move': fields.selection([('in', 'IN'), ('out', 'OUT')], 'Move', readonly=True , domain=[('move', '=', 'move')], help="Incoming or Outgoing Letter"),
        'move': fields.function(_get_direction, string='Move', type='selection', fnct_search=_search_direction, selection=DIRECTIONS, method=True, help="Incoming or Outgoing Letter"),
        'type': fields.many2one('letter.type', 'Type', help="Type of Letter, Depeding upon size", required=True), 
        'class': fields.many2one('letter.class', 'Class', help="Classification of Document"),
        'date': fields.datetime('Sent / Received Date', required=True),
        'formatted_date': fields.function(_formatted_date, string='Sent / Received Date', type='string', method=True, help="Formatted Date"),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'address_id': fields.many2one('res.partner.address', 'Address'),
        'user_id': fields.many2one('res.users', "Dispatcher", required=True),
        'snd_rec_id': fields.many2one('res.users', "Sender / Receiver"),
        'note': fields.text('Note'),
        'state': fields.selection([('draft', 'Draft'), ('rec', 'Received'), ('sent', 'Sent'), ('rec_bad', 'Received Damage'), ('rec_ret', 'Received But Returned'), ('cancel','Cancelled')], 'State', readonly=True),
        'parent_id': fields.many2one('res.letter', 'Parent'),
        'child_line': fields.one2many('res.letter', 'parent_id', 'Letter Lines'),
        'active': fields.boolean('Active'),
        'channel_id': fields.many2one('letter.channel', 'Sent / Receive Source'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'history_line': fields.one2many('letter.history', 'register_id', 'History'),
        'ref_data': fields.char('Reference Number', size=32, help="Reference Number Provided by postal provider."),
        'weight': fields.float('Weight (in KG)'),
        'size': fields.char('Size', size=64),
        'ref_ids': fields.one2many('letter.ref', 'letter_id', 'Reference'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,),
        'letter_text': fields.text('Letter Text'),
        'contact_id': fields.many2one('res.partner.address.contact', 'Contact'),
    }
    
    _defaults = {
        'number': _get_number,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, context: uid,
        'move': lambda self, cr, uid, context: context.get('move', 'in'),
        # 'state': lambda *a: 'draft',
        # 'active':lambda *a: 1,
        'state': 'draft',
        'active': True,
        'company_id': lambda self, cr, uid, c: self.pool['res.company']._company_default_get(cr, uid, 'res.letter', context=c),
    }

    _order = 'date desc'
    
    def create(self, cr, uid, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'company_id' not in values:
            if values['user_id']:
                user = self.pool['res.users'].browse(cr, uid, values['user_id'], context)
                values['company_id'] = user.company_id.id
        return super(res_letter, self).create(cr, uid, values, context)

    def copy(self, cr, uid, ids, default=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        default = default or {}
        default['number'] = self._get_number(cr, uid, context)
        res = super(res_letter, self).copy(cr, uid, ids, default, context)
        return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(res_letter, self).name_search(cr, uid, name, args, operator, context, limit)
        letter_ids = self.search(cr, uid, [('number', 'ilike', name)])
        return list(set(res + self.name_get(cr, uid, letter_ids)))
        
    def history(self, cr, uid, ids, context=None, keyword=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        lh_pool = self.pool['letter.history']
        for id in ids:
            lh_pool.create(cr, uid, {'name': keyword, 'user_id': uid, 'register_id': id}, context)
        return True
    
    def action_received(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'rec'}, context)
        self.history(cr, uid, ids, context={'translated_keyword': _('Received')}, keyword=_('Received'))
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'cancel'}, context)
        self.history(cr, uid, ids, context={'translated_keyword': _('Cancel')}, keyword=_('Cancel'))
        return True
    
    def action_sent(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'sent'}, context)
        self.history(cr, uid, ids, context={'translated_keyword': _('Sent')}, keyword=_('Sent'))
        return True
    
    def action_rec_ret(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'rec_ret'}, context)
        self.history(cr, uid, ids, context={'translated_keyword': _('Received But Returned')}, keyword=_('Received But Returned'))
        return True
    
    def action_rec_bad(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'rec_bad'}, context)
        self.history(cr, uid, ids, context={'translated_keyword': _('Received Damage')}, keyword=_('Received Damage'))
        return True
    
    def action_set_draft(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'draft'}, context)
        self.history(cr, uid, ids, context={'translated_keyword': _('Set To Draft')}, keyword=_('Set To Draft'))
        return True
