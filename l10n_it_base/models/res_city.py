# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2013 OpenERP Italian Community (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class res_city(orm.Model):
    _name = 'res.city'
    _description = 'City'

    _index_name = 'res_city_name_index'
    _index_zip = 'res_city_zip_index'

    def _auto_init(self, cr, context={}):
        super(res_city, self)._auto_init(cr, context)

        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s',
                   (self._index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON res_city (name)'.format(name=self._index_name))

        cr.execute('SELECT 1 FROM pg_indexes WHERE indexname=%s',
                   (self._index_zip,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX {name} ON res_city (zip)'.format(name=self._index_zip))

    _columns = {
        'name': fields.char('City', size=64, required=True),
        'province_id': fields.many2one('res.province', 'Province', ondelete='restrict'),
        'zip': fields.char('ZIP', size=5),
        'phone_prefix': fields.char('Telephone Prefix', size=16),
        'istat_code': fields.char('ISTAT code', size=16),
        'cadaster_code': fields.char('Cadaster Code', size=16),
        'web_site': fields.char('Web Site', size=64),
        'region': fields.related(
            'province_id', 'region', type='many2one', relation='res.region', string='Region', readonly=True),
    }
    _order = "name"

