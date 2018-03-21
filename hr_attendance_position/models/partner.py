# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

import logging

from openerp.osv import orm, fields
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
try:
    import googlemaps
except (ImportError, IOError) as err:
    _logger.error(err)


class ResPartnerAddress(orm.Model):
    _inherit = 'res.partner.address'

    _columns = {
        'latitude': fields.float('Latitude', digits=(8, 4)),
        'longitude': fields.float('Longitude', digits=(8, 4))
    }


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def action_get_coordinates(self, cr, uid, context):
        active_ids = context.get('active_ids', False)

        if active_ids:
            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id

            if company.google_key:
                gmaps = googlemaps.Client(key=company.google_key)

                for partner in self.browse(cr, uid, active_ids, context):
                    for address in partner.address:
                        google_address = u'{address.street}, {address.city} ({address.province.code}), {address.country_id.name}'.format(
                            address=address)
                        gres = gmaps.geocode(google_address)

                        latitude = gres[0]['geometry']['location']['lat']
                        longitude = gres[0]['geometry']['location']['lng']

                        if latitude and longitude and not address.latitude:
                            address.write({
                                'latitude': latitude,
                                'longitude': longitude
                            })
            else:
                raise orm.except_orm('Warning', _('Please set Google API key'))

        return True
