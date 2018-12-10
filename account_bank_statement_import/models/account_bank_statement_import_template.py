# -*- coding: utf-8 -*-
# © 2018 Antonio Mignolli - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class AccountBankStatementTemplate(orm.Model):

    _name = 'account.bank.statement.import.template'

    _description = 'Account Bank Statement Template'

    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'start_row': fields.integer('Start Row'),
        'col_description': fields.integer('Column No. with Description'),
        'col_operation_date': fields.integer('Column No. with Operation Date'),
        'col_value_date': fields.integer('Column No. with Value Date'),
        'col_value': fields.integer('Column No. with Value'),
        'col_causal': fields.integer('Column No. with Causal'),
        'rules': fields.one2many('account.bank.statement.import.template.rule', 'template_id', string='Rules')
    }


class AccountBankStatementTemplateRule(orm.Model):

    _name = 'account.bank.statement.import.template.rule'

    _description = 'Account Bank Statement Template Rule'

    _columns = {
        'template_id': fields.many2one('account.bank.statement.import.template', string='Template', readonly=True),
        'starts_with': fields.char(string='Row starts with', size=256),
        'account_id': fields.many2one('account.account', 'Account')
    }


