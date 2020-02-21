# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2019 Carlo Vettore (carlo.vettore at didotech.com)
import logging

import tools
from openerp.osv import fields, orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class crm_super_calendar(orm.Model):
    _description = "Super Calendar"
    _name = 'crm.super.calendar'
    _auto = False
    _rec = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', string='Partner'),
        'user_id': fields.many2one('res.users', string="User"),
        'date_action': fields.date('Date'),
        'source_id': fields.reference("Source Location", [
            ('crm.lead', 'Lead/Opportunity'),
            ('crm.meeting', 'Meeting'),
            ('crm.phonecall', 'Phone Call'),
            ('sale.order', 'Sale Order')
        ], size=128),
        'type': fields.selection([
            ('lead_opportunity', _('Lead/Opportunity')),
            ('crm_meeting', _('Meeting')),
            ('crm_phonecall', _('Phone Call')),
            ('sale_order', _('Sale Order'))], 'Type')
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'crm_super_calendar')
        try:
            cr.execute("""
                create or replace view crm_super_calendar AS (
                    SELECT 
                        row_number() OVER ()::INTEGER AS id,
                        *
                    FROM (
                        SELECT 
                            partner_id as partner_id,
                            user_id as user_id, 
                            date_action::DATE as date_action,
                            concat('crm.lead,', id) AS source_id,
                            'lead_opportunity' as type
                            from crm_lead
                            where state not in ('done') and date_action is not Null
                        
                        UNION
                        
                        SELECT 
                            partner_id as partner_id,
                            user_id as user_id, 
                            date::DATE as date_action,
                            concat('crm.meeting,', id) AS source_id,
                            'crm_meeting' as type
                            from crm_meeting
                            where state not in ('done', 'cancel') and date is not Null
                        
                        UNION
                        
                        SELECT 
                            partner_id as partner_id,
                            user_id as user_id, 
                            date::DATE as date_action,
                            concat('crm.phonecall,', id) AS source_id,
                            'crm_phonecall' as type
                            from crm_phonecall
                            where state not in ('done', 'cancel') and date is not Null
                        
                        UNION
                        
                        SELECT
                            partner_id as partner_id,
                            user_id as user_id, 
                            date_action_next::DATE as date_action,
                            concat('sale.order,', id) AS source_id,
                            'sale_order' as type
                            from sale_order
                            where state not in ('done', 'cancel') and date_action_next is not Null
                    ) as A        
                    ) 
            """)
        except Exception as e:
            _logger.error(u'Error: {error}'.format(error=e))

