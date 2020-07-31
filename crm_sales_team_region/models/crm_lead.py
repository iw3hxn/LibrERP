# -*- coding: utf-8 -*-
# © 2020 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class CrmLead(orm.Model):
    _inherit = 'crm.lead'

    def _get_user_from_crm_case_section(self, section_ids):
        user_ids = []
        for section in section_ids:
            if section.user_id:
                user_ids.append(section.user_id.id)
            for user in section.member_ids:
                user_ids.append(user.id)
        return user_ids

    def _get_regional_user_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for lead in self.browse(cr, uid, ids, context):
            user_ids = []
            if lead.partner_id and lead.partner_id.region_id:
                partner = lead.partner_id
                user_ids += self._get_user_from_crm_case_section(partner.region_id.crm_case_section_ids)

            if lead.region:
                user_ids += self._get_user_from_crm_case_section(lead.region.crm_case_section_ids)

            res[lead.id] = list(set(user_ids))
        return res

    def _search_regional_user_ids(self, cr, uid, obj, name, args, context=None):
        if args:
            partner_ids = []
            for arg in args:
                if arg[0] == 'regional_user_ids':
                    section_ids = self.pool['crm.case.section'].search(cr, uid, ['|', ('user_id', 'in', arg[2]), ('member_ids', 'in', arg[2])], context=context)
                    region_ids = self.pool['res.region'].search(cr, uid, [('crm_case_section_ids', 'in', section_ids)], context=context)
                    partner_ids = self.pool['res.partner'].search(cr, uid, [('address.region', 'in', region_ids)], context=context)
            return ['|', ('partner_id', 'in', partner_ids), ('region', 'in', region_ids)]
        return []

    _columns = {
        'regional_user_ids': fields.function(_get_regional_user_ids, type='one2many', relation='res.users', string="Regional Users", fnct_search=_search_regional_user_ids)
    }
