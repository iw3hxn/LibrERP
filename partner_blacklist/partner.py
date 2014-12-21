# -*- coding: utf-8 -*-

import time
from osv import fields
from osv import osv
from osv.orm import except_orm
from tools.translate import _

COLOR_SELECTION = [
         ('aqua', (u"Aqua")),
         ('black', (u"Black")),
         ('blue', (u"Blue")),
         ('brown', (u"Brown")),
         ('cadetblue', (u"Cadet Blue")),
         ('darkblue', (u"Dark Blue")),
         ('fuchsia', (u"Fuchsia")),
         ('forestgreen' , (u"Forest Green")),
         ('green', (u"Green")),
         ('grey', (u"Grey")),  
         ('red', (u"Red")),
         ('orange', (u"Orange"))
]


class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        partners = self.browse(cr, uid, ids)
        for partner in partners:
            if partner.blacklist:
                value[partner.id] = 'red'
            else:
                value[partner.id] = 'black'
        return value
    
    def onchange_blacklist(self, cr, uid, ids, blacklist, context=None):
        res = {}       
        if blacklist:
            res['sale_warn'] = 'warning'
        return {'value': res}
    
    _columns = {
        'blacklist': fields.boolean('Cliente bloccato', help="Ricorda di selezionare il messaggio da mostrare sui preventivi"),
        'row_color': fields.function(get_color, string = 'Row color', type='char', readonly=True, method=True,)
    }

