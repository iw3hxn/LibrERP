# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.  
#
##############################################################################

import time

import netsvc as netsvc
from openerp.osv import fields, orm
from tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from tools.translate import _


class mgmtsystem_nonconformity_location(orm.Model):
    _name = "mgmtsystem.nonconformity.location"
    _description = "Non Conformity Reference Locations"
    _order = "name"
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'active': fields.boolean('Active',
                                 help="If the active field is set to False, it will allow you to hide the sim allocation without removing it."),
        'model': fields.many2one('ir.model', 'Object', required=True),
    }
    _defaults = {
        'active': lambda *a: True,
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'model' in vals:
            raise orm.except_orm(_('Error !'), _(
                'You cannot modify the Object linked to the Document Type!\nCreate another Document instead !'))
        return super(mgmtsystem_nonconformity_location, self).write(cr, uid, ids, vals, context=context)


def _get_location(self, cr, uid, context=None):
    cr.execute('SELECT m.model, s.name FROM mgmtsystem_nonconformity_location s, ir_model m WHERE s.model = m.id ORDER BY s.name')
    return cr.fetchall()


class mgmtsystem_nonconformity_cause(orm.Model):
    """
    Cause of the nonconformity of the management system
    """
    _name = "mgmtsystem.nonconformity.cause"
    _description = "Cause of the nonconformity of the management system"
    _order = 'parent_id, sequence'

    def name_get(self, cr, uid, ids, context=None):
        ids = ids or []
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids, context=None, parent=None):
        return super(mgmtsystem_nonconformity_cause, self)._check_recursion(cr, uid, ids, context=context,
                                                                            parent=parent)

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Cause', size=50, required=True, translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence', help="Defines the order to present items"),
        'parent_id': fields.many2one('mgmtsystem.nonconformity.cause', 'Group'),
        'child_ids': fields.one2many('mgmtsystem.nonconformity.cause', 'parent_id', 'Child Causes'),
        'ref_code': fields.char('Reference Code', size=20),
    }
    _constraints = [
        (_check_recursion, 'Error! Cannot create recursive cycle.', ['parent_id'])
    ]


class mgmtsystem_nonconformity_origin(orm.Model):
    """
    Origin of nonconformity of the management system
    """
    _name = "mgmtsystem.nonconformity.origin"
    _description = "Origin of nonconformity of the management system"
    _order = 'parent_id, sequence'

    def name_get(self, cr, uid, ids, context=None):
        ids = ids or []
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids, context=None, parent=None):
        return super(mgmtsystem_nonconformity_origin, self)._check_recursion(cr, uid, ids, context=context,
                                                                             parent=parent)

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Origin', size=50, required=True, translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence', help="Defines the order to present items"),
        'parent_id': fields.many2one('mgmtsystem.nonconformity.origin', 'Group'),
        'child_ids': fields.one2many('mgmtsystem.nonconformity.origin', 'parent_id', 'Childs'),
        'ref_code': fields.char('Reference Code', size=20),
    }


class mgmtsystem_nonconformity_severity(orm.Model):
    """Nonconformity Severity - Critical, Major, Minor, Invalid, ..."""
    _name = "mgmtsystem.nonconformity.severity"
    _description = "Severity of Complaints and Nonconformities"
    _columns = {
        'name': fields.char('Title', size=50, required=True, translate=True),
        'sequence': fields.integer('Sequence', ),
        'description': fields.text('Description', translate=True),
        'active': fields.boolean('Active?'),
    }
    _defaults = {
        'active': True,
    }


_STATES = [
    ('draft', _('Draft')),
    ('analysis', _('Analysis')),
    ('pending', _('Pending Approval')),
    ('open', _('In Progress')),
    ('done', _('Closed')),
    ('cancel', _('Cancelled')),
]
_STATES_DICT = dict(_STATES)


class mgmtsystem_nonconformity(orm.Model):
    """
    Management System - Nonconformity 
    """
    _name = "mgmtsystem.nonconformity"
    _description = "Nonconformity of the management system"
    _rec_name = "ref"
    _inherit = ['mail.thread']
    _order = "date desc"

    def _state_name(self, cr, uid, ids, name, args, context=None):
        res = dict()
        for o in self.browse(cr, uid, ids, context=context):
            res[o.id] = _STATES_DICT.get(o.state, o.state)
        return res

    def _calculate_total_cost(self, cr, uid, ids, field_name, arg, context):
        ret = {}
        for nonconformity in self.browse(cr, uid, ids, context):
            tot = 0
            for cost in nonconformity.cost_ids:
                tot += cost.cost
            # TODO: VERIIFY WITH IMMEDIATE_ACTION cost!
            for action in nonconformity.action_ids:
                tot += action.cost
            ret[nonconformity.id] = tot
        return ret

    def _calculate_action_status(self, cr, uid, ids, field_name, arg, context):
        ret = {}
        action_obj = self.pool['mgmtsystem.action']

        for nonconformity in self.browse(cr, uid, ids, context):
            action_connnected_ids = action_obj.search(cr, uid, [('nonconformity_ids', '=', nonconformity.id)], context=context)
            if nonconformity.immediate_action_id:
                action_connnected_ids.append(nonconformity.immediate_action_id.id)
            action_closed_ids = action_obj.search(cr, uid, [('id', 'in', action_connnected_ids), ('state', '=', 'done')], context=context)

            ret[nonconformity.id] = {
                'action_date_close': False,
                'action_open': _(u'{0} of {1}').format(len(action_closed_ids), len(action_connnected_ids))
            }

        return ret

    _columns = {
        # 1. Description
        'id': fields.integer('ID', readonly=True),
        'ref': fields.char('Reference', size=64, required=True, readonly=True),
        'date': fields.date('Date', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'reference': fields.char('Related to', size=50),
        'reference_obj': fields.reference('Reference', selection=_get_location, size=None),
        'responsible_user_id': fields.many2one('res.users', 'Responsible', required=True),
        'manager_user_id': fields.many2one('res.users', 'Manager', required=True),
        'author_user_id': fields.many2one('res.users', 'Filled in by', required=True),
        'origin_ids': fields.many2many('mgmtsystem.nonconformity.origin', 'mgmtsystem_nonconformity_origin_rel',
                                       'nonconformity_id', 'origin_id', 'Origin'),
        'procedure_ids': fields.many2many('wiki.wiki', 'mgmtsystem_nonconformity_procedure_rel', 'nonconformity_id',
                                          'procedure_id', 'Procedure'),
        'description': fields.text('Description', required=True),
        'state': fields.selection(_STATES, 'State', readonly=True),
        'state_name': fields.function(_state_name, string='State Description', type='char', size=40),
        'system_id': fields.many2one('mgmtsystem.system', 'System'),
        'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model', '=', _name)]),
        # 2. Root Cause Analysis
        'cause_ids': fields.many2many('mgmtsystem.nonconformity.cause', 'mgmtsystem_nonconformity_cause_rel',
                                      'nonconformity_id', 'cause_id', 'Cause'),
        'severity_id': fields.many2one('mgmtsystem.nonconformity.severity', 'Severity'),
        'analysis': fields.text('Analysis'),
        # TODO: immediate_action_id seems useless, all goes into action_ids
        'immediate_action_id': fields.many2one('mgmtsystem.action', 'Immediate action',
                                               domain="[('nonconformity_id','=',id)]"),
        'analysis_date': fields.datetime('Analysis Date', readonly=True),
        'analysis_user_id': fields.many2one('res.users', 'Analysis by', readonly=True),
        # 3. Action Plan
        'action_ids': fields.many2many('mgmtsystem.action', 'mgmtsystem_nonconformity_action_rel', 'nonconformity_id',
                                       'action_id', 'Actions'),
        'actions_date': fields.datetime('Action Plan Date', readonly=True),
        'actions_user_id': fields.many2one('res.users', 'Action Plan by', readonly=True),
        'action_comments': fields.text('Action Plan Comments',
                                       help="Comments on the action plan."),
        # 4. Effectiveness Evaluation
        'evaluation_date': fields.datetime('Evaluation Date', readonly=True),
        'evaluation_user_id': fields.many2one('res.users', 'Evaluation by', readonly=True),
        'evaluation_comments': fields.text('Evaluation Comments',
                                           help="Conclusions from the last effectiveness evaluation."),
        # 5. Cost
        'cost_ids': fields.one2many('mgmtsystem.nonconformity.cost', 'mgmtsystem_nonconformity_id', string='Cost'),
        'cost_total': fields.function(_calculate_total_cost, method=True, type='float', string='Total Cost',
                                      help='Total cost of Nonconformity, sum of all nonconformities and actions costs'),
        # 6. Action connected
        'action_date_close': fields.function(_calculate_action_status, method=True, type='date', string='Date Close', multi='date_action'),
        'action_open': fields.function(_calculate_action_status, method=True, type='char', size=128, string='Close of', multi='date_action')
    }
    _defaults = {
        'date': lambda *a: time.strftime(DATE_FORMAT),
        'state': 'draft',
        'author_user_id': lambda cr, uid, id, c={}: id,
        'ref': 'NEW',
        'responsible_user_id': lambda obj, cr, uid, context: uid,
        'manager_user_id': lambda obj, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        vals.update({
            'ref': self.pool.get('ir.sequence').get(cr, uid, 'mgmtsystem.nonconformity')
        })
        return super(mgmtsystem_nonconformity, self).create(cr, uid, vals, context)

    def wkf_analysis(self, cr, uid, ids, context=None):
        """Change state from draft to analysis"""
        self.message_append(cr, uid, self.browse(cr, uid, ids), _('Analysis'))
        return self.write(cr, uid, ids, {'state': 'analysis', 'analysis_date': None, 'analysis_user_id': None},
                          context=context)

    def action_sign_analysis(self, cr, uid, ids, context=None):
        """Sign-off the analysis"""
        o = self.browse(cr, uid, ids, context=context)[0]
        if o.state != 'analysis':
            raise orm.except_orm(_('Error !'), _('This action can only be done in the Analysis state.'))
        if o.analysis_date:
            raise orm.except_orm(_('Error !'), _('Analysis is already approved.'))
        if not o.analysis:
            raise orm.except_orm(_('Error !'), _('Please provide an analysis before approving.'))
        vals = {'analysis_date': time.strftime(DATETIME_FORMAT), 'analysis_user_id': uid}
        self.write(cr, uid, ids, vals, context=context)
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Analysis Approved'))
        wf_service = netsvc.LocalService("workflow")
        cr.commit()
        for non_conformity_id in ids:
            wf_service.trg_validate(uid, 'mgmtsystem.nonconformity', non_conformity_id, 'button_review', cr)
        return True

    def wkf_review(self, cr, uid, ids, context=None):
        """Change state from analysis to pending approval"""
        o = self.browse(cr, uid, ids, context=context)[0]
        if not o.analysis_date:
            raise orm.except_orm(_('Error !'), _('Analysis must be performed before submiting to approval.'))
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Pending Approval'))
        return self.write(cr, uid, ids, {'state': 'pending', 'actions_date': None, 'actions_user_id': None},
                          context=context)

    def action_sign_actions(self, cr, uid, ids, context=None):
        """Sign-off the action plan"""
        o = self.browse(cr, uid, ids, context=context)[0]
        if o.state != 'pending':
            raise orm.except_orm(_('Error !'), _('This action can only be done in the Pending for Approval state.'))
        if o.actions_date:
            raise orm.except_orm(_('Error !'), _('Action plan is already approved.'))
        if not self.browse(cr, uid, ids, context=context)[0].analysis_date:
            raise orm.except_orm(_('Error !'), _('Analysis approved before the review confirmation.'))
        vals = {'actions_date': time.strftime(DATETIME_FORMAT), 'actions_user_id': uid}
        self.write(cr, uid, ids, vals, context=context)
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Action Plan Approved'))
        wf_service = netsvc.LocalService("workflow")
        cr.commit()
        for non_conformity_id in ids:
            wf_service.trg_validate(uid, 'mgmtsystem.nonconformity', non_conformity_id, 'button_open', cr)
        return True

    def wkf_open(self, cr, uid, ids, context=None):
        """Change state from pending approval to in progress, and Open  the related actions"""
        o = self.browse(cr, uid, ids, context=context)[0]
        if not o.actions_date:
            raise orm.except_orm(_('Error !'), _('Action plan must be approved before opening.'))
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('In Progress'))
        # Open related Actions
        if o.immediate_action_id and o.immediate_action_id.state == 'draft':
            o.immediate_action_id.case_open(cr, uid, [o.immediate_action_id.id])
        for a in o.action_ids:
            if a.state == 'draft':
                a.case_open(cr, uid, [a.id])
        return self.write(cr, uid, ids, {'state': 'open', 'evaluation_date': None, 'evaluation_user_id': None},
                          context=context)

    def action_sign_evaluation(self, cr, uid, ids, context=None):
        """Sign-off the effectiveness evaluation"""
        o = self.browse(cr, uid, ids, context=context)[0]
        if o.state != 'open':
            raise orm.except_orm(_('Error !'), _('This action can only be done in the In Progress state.'))
        vals = {'evaluation_date': time.strftime(DATETIME_FORMAT), 'evaluation_user_id': uid}
        self.write(cr, uid, ids, vals, context=context)
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Effectiveness Evaluation Approved'))
        wf_service = netsvc.LocalService("workflow")
        cr.commit()
        for non_conformity_id in ids:
            wf_service.trg_validate(uid, 'mgmtsystem.nonconformity', non_conformity_id, 'button_close', cr)
        return True

    def wkf_cancel(self, cr, uid, ids, context=None):
        """Change state to cancel"""
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Cancel'))
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def wkf_close(self, cr, uid, ids, context=None):
        """Change state from in progress to closed"""
        o = self.browse(cr, uid, ids, context=context)[0]
        if not o.evaluation_date:
            raise orm.except_orm(_('Error !'), _('Effectiveness evaluation must be performed before closing.'))
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Close'))
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def case_reset(self, cr, uid, ids, context=None, *args):
        """Reset to Draft and restart the workflows"""
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            res = wf_service.trg_create(uid, self._name, id, cr)
        self.message_append(cr, uid, self.browse(cr, uid, ids, context=context), _('Draft'))
        vals = {
            'state': 'draft',
            'analysis_date': None, 'analysis_user_id': None,
            'actions_date': None, 'actions_user_id': None,
            'evaluation_date': None, 'evaluation_user_id': None,
        }
        return self.write(cr, uid, ids, vals, context=context)


def _get_all_nonconformities(self, cr, uid, ids, field_name, arg, context):
    ret = {}
    for action in self.browse(cr, uid, ids, context):
        nonconformity_all_ids = action.nonconformity_ids
        if action.nonconformity_immediate_id:
            nonconformity_all_ids.append(action.nonconformity_immediate_id.id)
        ret[action.id] = [n.id for n in nonconformity_all_ids]
    return ret


def _get_all_partner_ids(self, cr, uid, ids, field_name, arg, context):
    ret = {}
    for action in self.browse(cr, uid, ids, context):
        ret[action.id] = [n.partner_id.id for n in action.nonconformity_all_ids]
    return ret


class mgmtsystem_action(orm.Model):
    _inherit = 'mgmtsystem.action'
    _columns = {
        'nonconformity_immediate_id': fields.many2one('mgmtsystem.nonconformity', 'immediate_action_id', readonly=True),
        'nonconformity_ids': fields.many2many(
            'mgmtsystem.nonconformity', 'mgmtsystem_nonconformity_action_rel', 'action_id', 'nonconformity_id',
            'Nonconformities', readonly=True),
        'nonconformity_all_ids': fields.function(_get_all_nonconformities, method=True, type='one2many',
                                                 relation='mgmtsystem.nonconformity', string="Non conformities"),
        'partner_ids': fields.function(_get_all_partner_ids, method=True, type='one2many', relation='res.partner', string='Partners'),
        'immediate_partner_id': fields.related('nonconformity_immediate_id', 'partner_id', relation='res.partner', string='Partner',
                                                help='If this action is immediate, this field is the partner associated to Nonconformity')
    }

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        search_ids = super(mgmtsystem_action, self).search(cr, uid, args, offset=offset,
                                                           limit=limit, order=order, context=context, count=count)
        partner_id = None
        for arg in args:
            if 'partner_id' in arg:
                partner_id = arg[2]
                break

        if not partner_id:
            return search_ids

        found_ids = []
        for action in self.browse(cr, uid, search_ids):
            partner_ids = [p.id for p in action.partner_ids]
            if partner_id in partner_ids:
                found_ids.append(action.id)
        return found_ids


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
