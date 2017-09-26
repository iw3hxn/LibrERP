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
import sys
import time
import traceback

from openerp.osv import orm, fields
from tools.translate import _

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


class letter_type(orm.Model):
    """Class to define various types for letters like: envelope, parcel, etc."""
    
    _name = 'letter.type'
    _description = "types for letters like: envelope, parcel, etc."
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        for use in self.browse(cr, uid, ids, context):
            if use.color:
                value[use.id] = use.color
            else:
                value[use.id] = 'black'
        return value

    _columns = {
        'name': fields.char('Type', size=32, required=True),
        'code': fields.char('Code', size=8, required=True),
        'active': fields.boolean('Active'),
        'move': fields.selection(DIRECTIONS, 'Move', help="Incoming or Outgoing Letter"),
        'color': fields.selection(COLOR_SELECTION, 'Color'),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True),
        'model': fields.many2one('ir.model', 'Model', required=False),
    }
    
    _defaults = {
        'active': True,  
    }
    
    _order = "code"
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]
        
    def get_letter_type(self, cr, uid, model, context=None):
        type_id = self.search(cr, uid, [('model', '=', model)], context=context)
        if type_id:
            return type_id[0]
        else:
            raise orm.except_orm('Warning', _('Please create letter type for model {0}').format(model,))


class letter_class(orm.Model):
    """ Class to define the classification of letter like: classified, confidential, personal, etc. """ 
    
    _name = 'letter.class'    
    _description = "letter like: classified, confidential, personal, etc."

    _columns = {
        'name': fields.char('Type', size=32, required=True),
        'active': fields.boolean('Active'),
    }
    
    _defaults = { 
        'active': True,  
    }
    
    _order = "name"
    

class letter_channel(orm.Model):
    """ Class to define various channels using which letters can be sent or received like: post, fax, email. """

    _name = 'letter.channel'
    ## Description can't be longer 64 chars
    _description = "channels using which letters can be sent/received like: post,fax"

    _columns = {
        'name': fields.char('Type', size=32, required=True),
        'active': fields.boolean('Active'),
    }

    _defaults = {  
        'active': True,  
    }
    
    _order = "name"
    

def _links_get(self, cr, uid, context=None):
    context = context or self.pool['res.users'].context_get(cr, uid)
    obj = self.pool['res.request.link']
    ids = obj.search(cr, uid, [], context=context)
    res = obj.browse(cr, uid, ids, context)
    return [(r.object, r.name) for r in res]


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

    _columns = {
        'name': fields.char('Subject', size=128, help="Subject of letter"),
        'number': fields.char('Number', size=32, help="Autogenerated Number of letter", required=True),
        # 'move': fields.selection([('in', 'IN'), ('out', 'OUT')], 'Move', readonly=True , domain=[('move', '=', 'move')], help="Incoming or Outgoing Letter"),
        'move': fields.function(_get_direction, string='Move', type='selection', fnct_search=_search_direction, selection=DIRECTIONS, method=True, help="Incoming or Outgoing Letter"),
        'type': fields.many2one('letter.type', 'Type', help="Type of Letter, Depeding upon size", required=True), 
        'class': fields.many2one('letter.class', 'Class', help="Classification of Document"),
        'date': fields.datetime('Sent / Received Date', required=True),
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
    
    def create(self, cr, uid, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'company_id' not in values:
            if values['user_id']:
                user = self.pool['res.users'].browse(cr, uid, values['user_id'], context)
                values['company_id'] = user.company_id.id
        return super(res_letter, self).create(cr, uid, values, context)
    
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
        

class letter_ref(orm.Model):
    _name = 'letter.ref'
    
    def _name_get_intref(self, cr, uid, ids, prop, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.int_ref.name_get()[0]
            res.append((record.id, name[1]))

        return dict(res)
        
    _columns = {
        'name': fields.char('Name', size=128, help="Subject of letter"),
        'int_ref': fields.reference('Reference', selection=_links_get, size=128),
        'ref_name': fields.function(_name_get_intref, method=True, type="char", string="Letter Reference"),
        'letter_id': fields.many2one('res.letter', "Letter"),
    }
    _defaults = {
        'name': lambda self, cr, uid, context: self.pool['ir.sequence'].get(cr, uid, 'letter.ref'),
    }


class hr_employee(orm.Model):
    _description = "Employee"
    _inherit = 'hr.employee'

    def _get_assigned_letters(self, cr, uid, ids, prop, unknow_none, context=None):
        if not len(ids):
            return {}
        model_name = super(hr_employee, self)._name
        res = []
        try:
            for id in ids:
                letter_ids = []
                ref_ids = self.pool['letter.ref'].search(cr, uid, [('int_ref', '=', model_name + ',' + str(id))], context=context)
                if ref_ids:
                    for ref in self.pool['letter.ref'].read(cr, uid, ref_ids, context=context):
                        letter_ids.append(ref['letter_id'][0])
                res.append((id, letter_ids))
        except:
            print repr(traceback.extract_tb(sys.exc_traceback))

        return dict(res)
    
    _columns = {
        'letter_ids': fields.function(_get_assigned_letters, method=True, string='Letter', type='one2many', relation="res.letter"),
    }


class letter_history(orm.Model):
    _name = "letter.history"
    _description = "Letter Communication History"
    _order = "id desc"

    _columns = {
        'register_id': fields.many2one('res.letter', 'Register'),
        'name': fields.char('Action', size=64),
        'date': fields.datetime('Date'),
        'user_id': fields.many2one('res.users', 'User Responsible', readonly=True),
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
