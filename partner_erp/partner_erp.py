# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2013 Camptocamp Austria (<http://camptocamp.com>).
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
from openerp.osv import fields, osv

class partner_erp(osv.osv):
    _name = "res.partner.erp"

    def _server_https(self, cr, uid, ids, name, args, context=None):
        res = {}
        for server in self.browse(cr, uid, ids, context=context):
            https = server.protocol + '://' + server.name
            if server.port:
                https += ':'+ str(server.port)
            if server.path:
                https += '/'+server.path
            https +='#'
            if server.user:
                https += 'login='+server.user
            if server.passwd:
                https += '&password='+server.passwd
            if server.db_name:
                https += '&db='+server.db_name
                
            res[server.id] = https
        return res

    _columns = {
          'partner_id'            : fields.many2one('res.partner', "Partner", required=True )
        , 'user_id'               : fields.many2one('res.users', "User", help="Keep empty for admin user" )
        , 'name'                  : fields.char    ('Server Name', size=32, required=True )
        , 'protocol'              : fields.selection([('http','http'),('https','https')],'Protocol', required=True )
        , 'port'                  : fields.integer ('Port' )
        , 'path'                  : fields.char    ('Path', size=32 )
        , 'db_name'               : fields.char    ('Database Name', size=32 ,required=True)
        , 'user'                  : fields.char    ('DB-User', size=16 )
        , 'passwd'                : fields.char    ('DB-Password', size=16 )
        , 'server_https'          : fields.function(_server_https, type='char', string='https command')
        }

    _defaults = {
     'protocol'             : lambda *a : 'https'
        }

partner_erp()


class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {
         'erp_ids' : fields.one2many('res.partner.erp','partner_id','ERP Info'),
      }

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

