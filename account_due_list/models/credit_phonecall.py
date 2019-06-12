# -*- encoding: utf-8 -*-

import time
from datetime import datetime

from openerp.addons.crm import crm
from openerp.osv import orm
from osv import fields
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class CreditPhonecall(orm.Model):
    _name = "credit.phonecall"
    _description = "Phonecall"
    _order = "date desc"
    _columns = {
        # From crm.case
        'name': fields.char('Call Summary', size=512, required=True),
        'active': fields.boolean('Active', required=False),
        'date_action_last': fields.datetime('Last Action', readonly=1),
        'date_action_next': fields.datetime('Next Action', readonly=1),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'partner_id': fields.many2one('res.partner', 'Partner', select=1),

        'company_id': fields.many2one('res.company', 'Company'),
        'description': fields.text('Description'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Todo'),
            ('cancel', 'Cancelled'),
            ('done', 'Held'),
            ('pending', 'Not Held'),
        ], 'State', size=16, readonly=True,
            help='The state is set to \'Todo\', when a case is created.\
                                      \nIf the case is in progress the state is set to \'Open\'.\
                                      \nWhen the call is over, the state is set to \'Held\'.\
                                      \nIf the call needs to be done then the state is set to \'Not Held\'.'),
        'date_open': fields.datetime('Opened', readonly=True),
        # phonecall fields
        'duration': fields.float('Duration', help="Duration in Minutes"),
        'priority': fields.selection(crm.AVAILABLE_PRIORITIES, 'Priority'),
        'date_closed': fields.datetime('Closed', readonly=True),
        'date': fields.datetime('Date', select=1),
    }

    def _get_default_state(self, cr, uid, context=None):
        if context and context.get('default_state', False):
            return context.get('default_state')
        return 'open'

    _defaults = {
        'date': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'priority': crm.AVAILABLE_PRIORITIES[2][0],
        'state': _get_default_state,
        'user_id': lambda self, cr, uid, ctx: uid,
        'active': 1,
    }

    # From crm.case

    def case_close(self, cr, uid, ids, context):
        """Overrides close for crm_case for setting close date
        """
        res = True
        for phone in self.browse(cr, uid, ids, context):
            phone_id = phone.id
            data = {'date_closed': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 'state': 'done'}
            if phone.duration <= 0:
                duration = datetime.now() - datetime.strptime(phone.date, DEFAULT_SERVER_DATETIME_FORMAT)
                data.update({'duration': duration.seconds / float(60)})
            self.write(cr, uid, [phone_id], data, context)
        return res

    def case_reset(self, cr, uid, ids, context):
        """Resets case as Todo
        """
        self.write(cr, uid, ids, {'duration': 0.0, 'state': 'open'}, context)
        return True

    def case_cancel(self, cr, uid, ids, context):
        """Resets case as Cancel
        """
        self.write(cr, uid, ids, {'duration': 0.0, 'state': 'cancel'}, context)
        return True

    def case_open(self, cr, uid, ids, context):
        """Overrides cancel for crm_case for setting Open Date
        """
        self.write(cr, uid, ids, {'date_open': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context)
        return True

    def case_pending(self, cr, uid, ids, context):
        """Resets case as Pending
        """
        self.write(cr, uid, ids, {'state': 'pending'}, context)
        return True

    def onchange_partner_id(self, cr, uid, ids, part, email=False, context=None):
        """This function returns value of partner address based on partner
        :param ids: List of case IDs
        :param part: Partner's id
        :param email: Partner's email ID
        """
        data = {}
        return {'value': data}

    def schedule_another_phonecall(self, cr, uid, ids, schedule_time, call_summary, \
                                   user_id=False, section_id=False, categ_id=False, action='schedule', context=None):
        """
        action :('schedule','Schedule a call'), ('log','Log a call')
        """
        model_data = self.pool.get('ir.model.data')
        phonecall_dict = {}
        if not categ_id:
            res_id = model_data._get_id(cr, uid, 'crm', 'categ_phone2')
            if res_id:
                categ_id = model_data.browse(cr, uid, res_id, context=context).res_id
        for call in self.browse(cr, uid, ids, context=context):
            if not section_id:
                section_id = call.section_id and call.section_id.id or False
            if not user_id:
                user_id = call.user_id and call.user_id.id or False
            vals = {
                'name': call_summary,
                'user_id': user_id or False,
                'categ_id': categ_id or False,
                'description': call.description or False,
                'date': schedule_time,
                'section_id': section_id or False,
                'partner_id': call.partner_id and call.partner_id.id or False,
                'partner_address_id': call.partner_address_id and call.partner_address_id.id or False,
                'partner_phone': call.partner_phone,
                'partner_mobile': call.partner_mobile,
                'priority': call.priority,
            }

            new_id = self.create(cr, uid, vals, context=context)
            self.case_open(cr, uid, [new_id])
            if action == 'log':
                self.case_close(cr, uid, [new_id])
            phonecall_dict[call.id] = new_id
        return phonecall_dict

