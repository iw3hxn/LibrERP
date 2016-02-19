# -*- coding: utf-8 -*-
##############################################################################
#    Daniel Reis
#
#    OpenERP, Open Source Management Solution
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
import pooler
from tools.safe_eval import safe_eval
from osv import fields, osv
from datetime import datetime
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

# TODO: implement this as an object, so it can be safely be accessed by
# "changed('state')" instead of "changed.get('state')"
DEFAULT_EVALDICT = {
    'old': {},
    'new': {},
    'changed': {},
    'creating': False,
    'inserting': False,
    'writing': False,
    'updating': False,
}

def get_datetime(date_field):
    '''Return a datetime from a date string or a datetime string'''
    #complete date time if date_field contains only a date
    date_split = date_field.split(' ')
    if len(date_split) == 1:
        date_field = date_split[0] + " 00:00:00"

    return datetime.strptime(date_field[:19], '%Y-%m-%d %H:%M:%S')


###############################################################################
# Base Action Rule
# (extends base_action_rule.py and crm_action_rule.py)
#
#   * format_mail() allows using additional fields in the email body:
#        ref, using %(object_ref)s
#        translated state name, using %(object_state)s
#        uppercase translated state name, using %(object_STATE)s
#   * email_send() allows a custom subject line, that should be provided
#     in the first line of the "body", using the prefix "Subject:".
#
###############################################################################
class base_action_rule(osv.osv):
    _inherit = 'base.action.rule'
    _columns = {
        'trg_evalexpr': fields.text('Evaluated expression',
            help='Python expression, able to use a "new" and "old" '
                 'dictionaries, with the changed columns.'),
        'trg_evalexpr_dbg': fields.boolean('Debug Evaluated expression',
            help='Write detailed information to log, to help debugging '
                 'trigger expressions.'),
        'email_template_id': fields.many2one('email.template',
            'E-mail template', domain="[('model_id','=',model_id)]"),
        'email_template_force': fields.boolean('Send immediately',
            help='If not checked, it will be sent the next time the e-mail '
                 'scheduler runs.'),
        'trg_date_field': fields.many2one('ir.model.fields', 'Comparison Date field',
                                         domain="['&',('ttype', 'in', ('date','datetime')),('model_id', '=', model_id)]"),

    }

    #overwrite of function
    def _check(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        """
        This Function is call by scheduler.
        """
        rule_pool = self.pool['base.action.rule']
        rule_ids = rule_pool.search(cr, uid, [], context=context)
        self._register_hook(cr, uid, rule_ids, context=context)

        rules = self.browse(cr, uid, rule_ids, context=context)
        for rule in rules:
            model = rule.model_id.model
            model_pool = self.pool.get(model)
            last_run = False
            if rule.last_run:
                last_run = get_datetime(rule.last_run)
            now = datetime.now()
            if not model_pool:
                continue
            for obj_id in model_pool.search(cr, uid, [], context=context):
                obj = model_pool.browse(cr, uid, obj_id, context=context)
                # Calculate when this action should next occur for this object
                base = False
                if rule.trg_date_field:
                    # data_trigger = hasattr(obj, 'create_date')
                    base = self.pool[obj._name].read(cr, uid, obj.id, [rule.trg_date_type.name], context=context)[
                        rule.trg_date_type.name]

                if base:
                    fnct = {
                        'minutes': lambda interval: timedelta(minutes=interval),
                        'day': lambda interval: timedelta(days=interval),
                        'hour': lambda interval: timedelta(hours=interval),
                        'month': lambda interval: timedelta(months=interval),
                    }
                    base = get_datetime(base)
                    delay = fnct[rule.trg_date_range_type](rule.trg_date_range)
                    action_date = base + delay

                    if not last_run or (last_run <= action_date < now):
                        print last_run
                        print action_date
                        print now
                        self._action(cr, uid, [rule.id], [obj], context=context)
            rule_pool.write(cr, uid, [rule.id], {'last_run': now},
                            context=context)

    def _check_evalexpr(self, cr, uid, ids, context=None):
        action = self.browse(cr, uid, ids[0], context=context)
        if action.trg_evalexpr:
            #Test if expression is valid, against an empty dict
            #Newlines are tolerated
            safe_eval(action.trg_evalexpr.replace('\n', ' '),
                {}, DEFAULT_EVALDICT)
        return True

    _constraints = [
        (_check_evalexpr,
            'Error: Your evaluated expression is not valid!',
            ['trg_evalexpr'])
    ]

    def _create(self, old_create, model, context=None):
        """
        Return a wrapper around `old_create` calling both `old_create` and
        `post_action`, in that order.
        """
        def wrapper(cr, uid, vals, context=context):
            if context is None:
                context = self.pool['res.users'].context_get(cr, uid)
            # store new and old values in context, to use in trigger expr.
            # _action_trigger=create prevents write trigger to fire
            context.update({
                '_action_old': {},
                '_action_new': vals,
                '_action_trigger': 'create',
            })
            new_id = old_create(cr, uid, vals, context=context)
            if not context.get('action'):
                self.post_action(cr, uid, [new_id], model, context=context)
            return new_id
        return wrapper

    def _write(self, old_write, model, context=None):
        """
        Return a wrapper around `old_write` calling both `old_write` and
        `post_action`, in that order.
        """
        def wrapper(cr, uid, ids, vals, context=context):
            if context is None:
                context = self.pool['res.users'].context_get(cr, uid)
            if isinstance(ids, (str, int, long)):
                ids = [ids]
            # store new and old values in context, to use in trigger expr.
            olds = self.pool.get(model).read(cr, uid, ids, context=context)
            context.update({
                '_action_old': olds,
                '_action_new': vals,
            })
            old_write(cr, uid, ids, vals, context=context)
            if (not context.get('action') and
                not context.get('_action_trigger')):
                context.update({'_action_trigger': 'write'})  # trg.activated
                self.post_action(cr, uid, ids, model, context=context)
            return True
        return wrapper

    # Actions can be triggered from evaluated expression,
    # using values from dictionaries 'old' and 'new'
    # new:   is the dictionay passed to the create/write method,
    #        therefore it contains only the fields to write.
    # old:   on create is an empty dict or None value; on write constains the
    #        values before the write is executed, given by the read() method
    # Example: to check if responsible changed:
    #         not old and old['user_id']!=new['user_id']
    def do_check(self, cr, uid, action, obj, context={}):
        ok = super(base_action_rule, self)\
            .do_check(cr, uid, action, obj, context=context)
        if ok and action.trg_evalexpr:
            ok = False
            if context.get('_action_trigger'):
                is_ins = context.get('_action_trigger') == 'create'
                #If no changed values, exit with False
                #Abort if called from crm_case._action, to duplicate triggering
                if not context.get('_action_new') or context.get('state_to'):
                    return False
                #old dict: holds original values for all columns
                #(before the write/update)
                old = {}
                for x in context.get('_action_old'):
                    if x.get('id') == obj.id:  # Old is a list of records
                        old = x
                        break
                #Normalize tuples (id, name) on "old" into id only form
                for x in old:
                    if isinstance(old[x], tuple):
                        old[x] = old[x][0]
                # changed dict: holds only the changed values;
                # available only on write/update
                changed = {}
                if not is_ins:
                    for k, v in context.get('_action_new').items():
                        #rint '\t', k, ':', v, '<=', old.get(k)
                        if old.get(k) != v:
                            changed.update({k: v})
                # new dict: result of applying changes to old
                # (includes non changed values)
                new = dict(old)  # copy dict content, not dict pointer
                new.update(changed)
                #Evaluate trigger expression
                eval_dict = dict(DEFAULT_EVALDICT)
                eval_dict.update({
                    'obj': obj,  # allows object.notation
                    'old': old,
                    'changed': changed,
                    'new': new,
                    'inserting': is_ins, 'creating': is_ins,
                    'updating': not is_ins, 'writing': not is_ins,
                    })
                if action.trg_evalexpr_dbg:
                    _logger.setLevel(logging.DEBUG)
                    _logger.debug('Rule CHECK: %s on record id %d.'
                        % (action.name, obj.id))
                    _logger.debug('CHG: %s' % str(changed))
                    _logger.debug('NEW: %s' % str(new))
                    _logger.debug('OLD: %s' % str(old))
                #try: ...removed; leaving eval errors unhandled...
                ok = safe_eval(action.trg_evalexpr.replace('\n', ' '),
                    {}, eval_dict)
                if ok:
                    _logger.debug('RULE ACTIVATED: %s on record id %d.'
                        % (action.name, obj.id))
                else:
                    if action.trg_evalexpr_dbg:
                        _logger.debug('Rule not activated: %s on record id %d.'
                            % (action.name, obj.id))
        return ok

    #Action able to send e-mails using email_template;
    #Bonus: messages sent are recorded in the communication history.
    def do_action(self, cr, uid, action, model_obj, obj, context=None):
        _logger.debug('Rule do_action: %s on record id %d.'
            % (action.name, obj.id))
        super(base_action_rule, self).do_action(
            cr, uid, action, model_obj, obj, context=context)
        if action.email_template_id:
            _logger.debug('Rule sending mail: using template %s.'
                % (action.email_template_id.name))
            mail_template = self.pool.get('email.template')
            mail_message = self.pool.get('mail.message')
            msg_id = mail_template.send_mail(
                cr, uid, action.email_template_id, obj.id, context=context)
            #mail_template does not set the e-mail date by itself!
            mail_message.write(cr, uid, [msg_id],
                {'date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
            #send immediatly, if the option is checked
            if action.email_template_force:
                mail_message.send(cr, uid, [msg_id], context=context)
        return True

base_action_rule()


#Force register hooks on user Login, to not depend on scheduler
#BUG https://bugs.launchpad.net/openobject-addons/+bug/944197
class users(osv.osv):
    _inherit = "res.users"

    def login(self, db, login, password):
        #Perform login
        user_id = super(users, self).login(db, login, password)
        #Register hooks
        cr = pooler.get_db(db).cursor()
        rule_pool = pooler.get_pool(db).get('base.action.rule')
        rule_ids = rule_pool.search(cr, 1, [])
        rule_pool._register_hook(cr, 1, rule_ids)
        rule_ids = None
        cr.close()
        #End
        return user_id
users()
