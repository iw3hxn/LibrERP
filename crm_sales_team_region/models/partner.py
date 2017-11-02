# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def create(self, cr, uid, values, context=None):
        city_model = self.pool['res.city']
        if 'address' in values and not values.get('section_id', False):
            for address in values['address']:
                if address[0] == 0 and address[2].get('city', False):
                    # find Sale Team and assign section_id
                    city_ids = city_model.search(
                        cr, uid, [('name', '=ilike', address[2]['city'])]
                    )
                    if city_ids:
                        city = city_model.browse(cr, uid, city_ids[0], context)
                        region_id = city.province_id.region.id
                        section_ids = self.pool['crm.case.section'].search(
                            cr, uid, [('region_ids', '=', region_id)])
                        if section_ids:
                            values['section_id'] = section_ids[0]
                            break
        return super(ResPartner, self).create(cr, uid, values, context)

    def write(self, cr, uid, ids, values, context=None):
        city_model = self.pool['res.city']
        for partner in self.browse(cr, uid, ids, context):
            if 'address' in values:
                if partner.customer and not partner.section_id \
                        and not values.get('section_id', False):
                        # or ('section_id' in values and not values['section_id']):
                    for address in values['address']:
                        if address[0] == 0 and address[2].get('city', False):
                            # find Sale Team and assign section_id
                            city_ids = city_model.search(
                                cr, uid, [('name', '=ilike', address[2]['city'])]
                            )
                            if city_ids:
                                city = city_model.browse(cr, uid, city_ids[0], context)
                                region_id = city.province_id.region.id
                                section_ids = self.pool['crm.case.section'].search(
                                    cr, uid, [('region_ids', '=', region_id)])
                                if section_ids:
                                    partner.write({'section_id': section_ids[0]})
                                    if 'section_id' in values:
                                        del values['section_id']
                                    break

        return super(ResPartner, self).write(cr, uid, ids, values, context)
