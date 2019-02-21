# -*- encoding: utf-8 -*-
import oerplib

oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)
oerp.login('admin', 'admin', 'admin')

ACCOUNT_INVOICE = 'account.invoice'
PARTNER = 'res.partner'
ACCOUNT_MOVE_LINE = 'account.move.line'
ACCOUNT_BANK_STATEMENT_LINE = 'account.bank.statement.line'
ACCOUNT_ACCOUNT = 'account.account'

res_partner_obj = oerp.get(PARTNER)
account_invoice_obj = oerp.get(ACCOUNT_INVOICE)
account_move_line_obj = oerp.get(ACCOUNT_MOVE_LINE)
account_bank_statement_line_obj = oerp.get(ACCOUNT_BANK_STATEMENT_LINE)
account_account_obj = oerp.get(ACCOUNT_ACCOUNT)

new_account_id = 226
partner_ids = res_partner_obj.search([('customer', '=', True), ('property_account_receivable', '!=', new_account_id)])

print("CUSTOMER")

for partner in res_partner_obj.browse(partner_ids):
    account_id = partner.property_account_receivable.id

    try:
        res_partner_obj.write(partner.id, {'property_account_receivable': new_account_id})

        account_invoice_ids = account_invoice_obj.search([('account_id', '=', account_id)])
        account_invoice_obj.write(account_invoice_ids, {'account_id': new_account_id})

        account_move_line_ids = account_move_line_obj.search([('account_id', '=', account_id)])
        account_move_line_obj.write(account_move_line_ids, {'account_id': new_account_id}, context={'force_sanitize': True})

        account_bank_statement_line_ids = account_bank_statement_line_obj.search([('account_id', '=', account_id)])
        account_bank_statement_line_obj.write(account_bank_statement_line_ids, {'account_id': new_account_id})

        account_account_obj.unlink([account_id])

        print("Update {0}".format(partner.name))
    except Exception as e:
        print("Error {0}".format(partner.name))
        print(e)

new_account_id = 382
partner_ids = res_partner_obj.search([('supplier', '=', True), ('property_account_payable', '!=', new_account_id)])

for partner in res_partner_obj.browse(partner_ids):
    account_id = partner.property_account_receivable.id

    try:
        res_partner_obj.write(partner.id, {'property_account_payable': new_account_id})

        account_invoice_ids = account_invoice_obj.search([('account_id', '=', account_id)])
        account_invoice_obj.write(account_invoice_ids, {'account_id': new_account_id})

        account_move_line_ids = account_move_line_obj.search([('account_id', '=', account_id)])
        account_move_line_obj.write(account_move_line_ids, {'account_id': new_account_id},
                                    context={'force_sanitize': True})

        account_bank_statement_line_ids = account_bank_statement_line_obj.search([('account_id', '=', account_id)])
        account_bank_statement_line_obj.write(account_bank_statement_line_ids, {'account_id': new_account_id})

        account_account_obj.unlink([account_id])

        print("Update {0}".format(partner.name))
    except Exception as e:
        print("Error {0}".format(partner.name))
        print(e)



