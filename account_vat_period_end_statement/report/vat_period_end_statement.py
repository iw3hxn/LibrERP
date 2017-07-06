# -*- coding: utf-8 -*-
#    Copyright (C) 2011-12 Domsense s.r.l. <http://www.domsense.com>.
#    Copyright (C) 2012-15 Agile Business Group sagl <http://www.agilebg.com>
#    Copyright (C) 2013-15 LinkIt Spa <http://http://www.linkgroup.it>
#    Copyright (C) 2013-17 Associazione Odoo Italia
#                          <http://www.odoo-italia.org>
#    Copyright (C) 2017    Didotech srl <http://www.didotech.com>
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
import time
from report import report_sxw
from tools.translate import _
from openerp.osv import orm


class print_vat_period_end_statement(report_sxw.rml_parse):
    _name = 'parser.vat.period.end.statement'

    def _build_codes_dict(self, tax_code, res=None, context=None):
        if res is None:
            res = {}
        if context is None:
            context = {}
        tax_pool = self.pool.get('account.tax')
        if tax_code.sum_period:
            if res.get(tax_code.name, False):
                raise orm.except_orm(
                    _('Error'),
                    _('Too many occurences of tax code %s') % tax_code.name)
            # search for taxes linked to that code
            tax_ids = tax_pool.search(
                self.cr, self.uid, [
                    ('tax_code_id', '=', tax_code.id)], context=context)
            if tax_ids:
                tax = tax_pool.browse(
                    self.cr, self.uid, tax_ids[0], context=context)
                # search for the related base code
                base_code = (
                    tax.base_code_id or tax.parent_id and
                    tax.parent_id.base_code_id or False)
                if not base_code:
                    raise orm.except_orm(
                        _('Error'),
                        _('No base code found for tax code %s')
                        % tax_code.name)
                # check if every tax is linked to the same tax code and base
                # code
                for tax in tax_pool.browse(
                    self.cr, self.uid, tax_ids, context=context
                ):
                    test_base_code = (
                        tax.base_code_id or tax.parent_id and
                        tax.parent_id.base_code_id or False)
                    if test_base_code.id != base_code.id:
                        raise orm.except_orm(
                            _('Error'),
                            _('Not every tax linked to tax code %s is linked '
                              'the same base code') % tax_code.name)
                res[tax_code.name] = {
                    'vat': tax_code.sum_period,
                    'base': base_code.sum_period,
                }
            for child_code in tax_code.child_ids:
                res = self._build_codes_dict(
                    child_code, res=res, context=context)
        return res

    def _get_tax_codes_amounts(
        self, period_id, tax_code_ids=None, context=None
    ):
        if tax_code_ids is None:
            tax_code_ids = []
        if context is None:
            context = {}
        res = {}
        code_pool = self.pool.get('account.tax.code')
        context['period_id'] = period_id
        for tax_code in code_pool.browse(
            self.cr, self.uid, tax_code_ids, context=context
        ):
            res = self._build_codes_dict(tax_code, res=res, context=context)
        return res

    def find_period(self, date, context=None):
        if context is None:
            context = {}
        period_pool = self.pool.get('account.period')
        period_ids = period_pool.find(
            self.cr, self.uid, dt=date, context=context)
        if len(period_ids) > 1:
            raise orm.except_orm(
                _('Error'), _('Too many periods for date %s') % str(date))
        return period_ids[0]

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(print_vat_period_end_statement, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'tax_codes_amounts': self._get_tax_codes_amounts,
            'find_period': self.find_period,
        })
        self.context = context


report_sxw.report_sxw(
    'report.account.print.vat.period.end.statement',
    'account.vat.period.end.statement',
    'addons/account_vat_period_end_statement/report/'
    'vat_period_end_statement.mako',
    parser=print_vat_period_end_statement)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
