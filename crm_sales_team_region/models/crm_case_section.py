# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class CrmCaseSection(orm.Model):
    _inherit = 'crm.case.section'

    _columns = {
        'region_ids': fields.many2many('res.region', 'crm_case_section_res_region_rel', 'crm_case_section_id', 'res_region_id', string='Regions')
    }
