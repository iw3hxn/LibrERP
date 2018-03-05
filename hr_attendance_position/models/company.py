# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields, orm


class ResCompany(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'google_key': fields.char('Google API key', size=64, help="""To create your key:
            - Visit the APIs console at Google APIs Console (https://console.developers.google.com) and log in with your Google Account.
            - Click the Services link from the left-hand menu in the APIs Console, then activate the Google Maps Geocoding API service.
            - Once the service has been activated, your API key is available from the API Access page, in the Simple API Access section. 
            Distance Matrix API applications use the Key for server apps
        """)
    }
