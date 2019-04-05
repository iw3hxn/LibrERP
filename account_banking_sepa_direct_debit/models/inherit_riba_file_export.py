# -*- coding: utf-8 -*-

import base64
import logging

from openerp.osv import fields, orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try:
    import fintech
    fintech.register()
    from fintech.sepa import Account, SEPADirectDebit

except ImportError:
    _logger.debug('Cannot `import fintech`.')

from lxml import etree


class riba_file_export(orm.Model):
    _inherit = "riba.file.export"

    def act_getfile(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        order_obj = self.pool['riba.distinta'].browse(cr, uid, active_ids, context=context)[0]
        if order_obj.sdd:
            # Create the creditor account from a tuple (ACCOUNT, BANKCODE)
            creditor = Account(iban=order_obj.config.bank_id.acc_number.replace(' ', ''), name=order_obj.config.bank_id.partner_id.name)
            # Assign the creditor id
            creditor.set_creditor_id(order_obj.config.PrvtId)
            # Create a SEPADirectDebit instance of type CORE
            # sdd = SEPADirectDebit(account=creditor, type='CORE', pain_scheme='pain.008.001.02-CBI-IT')
            sdd = SEPADirectDebit(account=creditor, type='CORE')
            # sdd.pain_scheme = 'pain.008.001.02-CBI-IT'
            for line in order_obj.line_ids:
                # Create the debtor account from a tuple (IBAN, BIC)
                if line.mandate_id.partner_bank_id:
                    debtor = Account(iban=line.mandate_id.partner_bank_id.acc_number.replace(' ', ''), name=line.partner_id.name)
                    # For a SEPA direct debit a valid mandate is required
                    debtor.set_mandate(mref=line.mandate_id.unique_mandate_reference, signed=line.mandate_id.signature_date, recurrent=True)
                    # Add the transaction
                    print(line.sequence)
                    sdd.add_transaction(account=debtor, amount=line.amount, purpose=line.invoice_number, eref=u'{0}'.format(str(line.sequence)), due_date=line.due_date)
                else:
                    print "pippo"

            # Render the SEPA document
            out = base64.encodestring(sdd.render().encode("iso-8859-1"))

            return self.write(cr, uid, ids, {'state': 'get', 'riba_.txt': out}, context=context)
        else:
            return super(riba_file_export, self).act_getfile(cr, uid, ids, context)

    def create_sepa(self, cr, uid, ids, context=None):
        """Creates the SEPA Direct Debit file. That's the important code !"""
        context = {} if context is None else context
        sepa_export = self.browse(cr, uid, ids[0], context=context)
        # Get country id for any customization
        country_id, country_code = self.pool['res.company']._get_country(cr, uid, sepa_export.payment_order_ids[0].company_id.id)


        pain_flavor = sepa_export.payment_order_ids[0].mode.type.code
        pain_name = sepa_export.payment_order_ids[0].mode.type.name
        convert_to_ascii = sepa_export.payment_order_ids[0].mode.convert_to_ascii
        # code to manage variant schema (i.e. Italian banks in CBI)
        pain_xsd_file, variant = self._get_pain_file_name(
            pain_name, pain_flavor)
        bic_xml_tag, name_maxsize, root_xml_tag = self._get_pain_tags(
            pain_flavor, variant=variant)
        gen_args = {
            'bic_xml_tag': bic_xml_tag,
            'name_maxsize': name_maxsize,
            'convert_to_ascii': convert_to_ascii,
            'payment_method': 'DD',
            'pain_flavor': pain_flavor,
            'sepa_export': sepa_export,
            'file_obj': self.pool['banking.export.sdd'],
            'pain_xsd_file': pain_xsd_file,
            'variant_xsd': variant,
            'country': country_code
        }
        pain_ns, root_name = self._get_nsmap(pain_xsd_file, pain_flavor)
        xml_root = etree.Element(root_name, nsmap=pain_ns)
        if root_xml_tag:
            pain_root = etree.SubElement(xml_root, root_xml_tag)
        else:
            pain_root = xml_root
        # A. Group header
        group_header_1_0, nb_of_transactions_1_6, control_sum_1_7 = \
            self.generate_group_header_block(
                cr, uid, pain_root, gen_args)
        transactions_count_1_6 = 0
        total_amount = 0.0
        amount_control_sum_1_7 = 0.0
        lines_per_group = {}
        # key = (requested_date, priority, sequence type)
        # value = list of lines as objects
        # Iterate on payment orders
        today = fields.date.context_today(self, cr, uid, context=context)
        for payment_order in sepa_export.payment_order_ids:
            total_amount = total_amount + payment_order.total
            # Iterate each payment lines
            for line in payment_order.line_ids:
                transactions_count_1_6 += 1
                priority = line.priority
                if payment_order.date_prefered == 'due':
                    requested_date = line.ml_maturity_date or today
                elif payment_order.date_prefered == 'fixed':
                    requested_date = payment_order.date_scheduled or today
                else:
                    requested_date = today
                if not line.mandate_id:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Missing SEPA Direct Debit mandate on the payment "
                          "line with partner '%s' and Invoice ref '%s'.")
                        % (line.partner_id.name,
                           line.ml_inv_ref.number))
                scheme = line.mandate_id.scheme
                if line.mandate_id.state != 'valid':
                    raise orm.except_orm(
                        _('Error:'),
                        _("The SEPA Direct Debit mandate with reference '%s' "
                          "for partner '%s' has expired.")
                        % (line.mandate_id.unique_mandate_reference,
                           line.mandate_id.partner_id.name))
                if line.mandate_id.type == 'oneoff':
                    if not line.mandate_id.last_debit_date:
                        seq_type = 'OOFF'
                    else:
                        raise orm.except_orm(
                            _('Error:'),
                            _("The mandate with reference '%s' for partner "
                              "'%s' has type set to 'One-Off' and it has a "
                              "last debit date set to '%s', so we can't use "
                              "it.")
                            % (line.mandate_id.unique_mandate_reference,
                               line.mandate_id.partner_id.name,
                               line.mandate_id.last_debit_date))
                elif line.mandate_id.type == 'recurrent':
                    seq_type_map = {
                        'recurring': 'RCUR',
                        'first': 'FRST',
                        'final': 'FNAL',
                    }
                    seq_type_label = \
                        line.mandate_id.recurrent_sequence_type
                    assert seq_type_label is not False
                    seq_type = seq_type_map[seq_type_label]

                key = (requested_date, priority, seq_type, scheme)
                if key in lines_per_group:
                    lines_per_group[key].append(line)
                else:
                    lines_per_group[key] = [line]
                # Write requested_exec_date on 'Payment date' of the pay line
                if requested_date != line.date:
                    self.pool['payment.line'].write(
                        cr, uid, line.id,
                        {'date': requested_date}, context=context)

        for (requested_date, priority, sequence_type, scheme), lines in \
                lines_per_group.items():
            # B. Payment info
            payment_info_2_0, nb_of_transactions_2_4, control_sum_2_5 = \
                self.generate_start_payment_info_block(
                    cr, uid, pain_root,
                    "sepa_export.payment_order_ids[0].reference + '-' + "
                    "sequence_type + '-' + requested_date.replace('-', '')  "
                    "+ '-' + priority",
                    priority, scheme, sequence_type, requested_date, {
                        'sepa_export': sepa_export,
                        'sequence_type': sequence_type,
                        'priority': priority,
                        'requested_date': requested_date,
                    }, gen_args, context=context)

            if variant == 'CBI-IT':
                self.generate_party_block(
                    cr, uid, payment_info_2_0, 'Cdtr', 'B',
                    'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.'
                    'name',
                    'sepa_export.payment_order_ids[0].mode.bank_id.acc_number',
                    'sepa_export.payment_order_ids[0].mode.bank_id.bank.bic',
                    {'sepa_export': sepa_export},
                    gen_args,
                    sepa_credid='sepa_export.payment_order_ids[0].company_id.'
                                'sepa_creditor_identifier',
                    context=context)
            else:
                charge_bearer_2_24 = etree.SubElement(payment_info_2_0,
                                                      'ChrgBr')
                charge_bearer_2_24.text = sepa_export.charge_bearer
                self.generate_party_block(
                    cr, uid, payment_info_2_0, 'Cdtr', 'B',
                    'sepa_export.payment_order_ids[0].mode.bank_id.partner_id.'
                    'name',
                    'sepa_export.payment_order_ids[0].mode.bank_id.acc_number',
                    'sepa_export.payment_order_ids[0].mode.bank_id.bank.bic',
                    {'sepa_export': sepa_export},
                    gen_args,
                    context=context)
            creditor_scheme_identification_2_27 = etree.SubElement(
                payment_info_2_0, 'CdtrSchmeId')
            self.generate_creditor_scheme_identification(
                cr, uid, creditor_scheme_identification_2_27,
                'sepa_export.payment_order_ids[0].company_id.'
                'sepa_creditor_identifier',
                'SEPA Creditor Identifier', {'sepa_export': sepa_export},
                'SEPA', gen_args)
            transactions_count_2_4 = 0
            amount_control_sum_2_5 = 0.0
            for line in lines:
                transactions_count_2_4 += 1
                amount_control_sum_1_7 += line.amount_currency
                amount_control_sum_2_5 += line.amount_currency
                dd_transaction_info_2_28 = self._get_trx_info(
                    cr, uid,
                    line, payment_info_2_0, sequence_type, gen_args,
                    sepa_export, bic_xml_tag,
                    variant=variant, context=context)
                self.generate_party_block(
                    cr, uid, dd_transaction_info_2_28, 'Dbtr', 'C',
                    'line.partner_id.name',
                    'line.bank_id.acc_number',
                    'line.bank_id.bank.bic',
                    {'line': line}, gen_args)

                self.generate_remittance_info_block(
                    cr, uid, dd_transaction_info_2_28,
                    line, gen_args)
            if nb_of_transactions_2_4:
                nb_of_transactions_2_4.text = unicode(transactions_count_2_4)
            if control_sum_2_5:
                control_sum_2_5.text = '%.2f' % amount_control_sum_2_5
        nb_of_transactions_1_6.text = unicode(transactions_count_1_6)
        control_sum_1_7.text = '%.2f' % amount_control_sum_1_7

        return self.finalize_sepa_file_creation(
            cr, uid, ids, xml_root, total_amount, transactions_count_1_6,
            gen_args, context=context)