# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class ResRegion(orm.Model):
    _inherit = 'res.region'

    _columns = {
        'crm_case_section_ids': fields.many2many('crm.case.section', 'crm_case_section_res_region_rel', 'res_region_id', 'crm_case_section_id', string='Sales Team')
    }
