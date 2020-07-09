# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def _get_regional_user_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            user_ids = []
            if partner.region_id:
                for section in partner.region_id.crm_case_section_ids:
                    if section.user_id:
                        user_ids.append(section.user_id.id)
                    for user in section.member_ids:
                        user_ids.append(user.id)
            res[partner.id] = list(set(user_ids))
        return res

    def _search_regional_user_ids(self, cr, uid, obj, name, args, context=None):
        if args:
            partner_ids = []
            for arg in args:
                if arg[0] == 'regional_user_ids':
                    section_ids = self.pool['crm.case.section'].search(cr, uid, ['|', ('user_id', 'in', arg[2]), ('member_ids', 'in', arg[2])], context=context)
                    region_ids = self.pool['res.region'].search(cr, uid, [('crm_case_section_ids', 'in', section_ids)], context=context)
                    partner_ids = self.search(cr, uid, [('region_id', 'in', region_ids)], context=context)
            return [('id', 'in', partner_ids)]
        return []

    _columns = {
        'region_id': fields.related('address', 'region', type='many2one', relation='res.region', string='Region'),
        'regional_user_ids': fields.function(_get_regional_user_ids, type='one2many', relation='res.users', string="Regional Users", fnct_search=_search_regional_user_ids)
    }

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
