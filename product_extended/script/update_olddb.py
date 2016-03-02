__author__ = 'carlo'
__version__ = '1.0.0'

import oerplib


def update_module(oerp):
    invoice_obj = oerp.get('account.invoice')
    invoice_ids = invoice_obj.search([('type', 'in', ['out_invoice', 'in_invoice'])], order="date_invoice asc")
    invoice_obj.update_product(invoice_ids)
    print 'Invoice Done'

    order_obj = oerp.get('sale.order')
    order_ids = order_obj.search([('state', 'in', ['manual', 'progress', 'done'])], order="date_order asc")
    order_obj.update_product(order_ids)
    print 'Sale Order Done'

    purchase_obj = oerp.get('purchase.order')
    purchase_ids = purchase_obj.search([('state', 'in', ['done'])], order="date_order asc")
    purchase_obj.update_product(purchase_ids)
    print 'Purchase Done'

    exit()


def show_db(conn):
    list_db = conn.db.list()
    index = 0
    for db in list_db:
        print "%s : %s" % (index, db)
        index += 1
    print "Q : exit"

    is_valid = 0
    while not is_valid:
        try:
            choice = raw_input("Insert Number of DB : ")
            if choice == 'Q':
                exit()
            choice = int(choice)
            is_valid = 1
        except ValueError, e:
            print ("'%s' is not a valid integer." % e.args[0].split(": ")[1])

    return list_db[choice]


def connect_db(oerp, database):
    print "Database : %s" % database
    user = raw_input("User: ")
    passwd = raw_input("Password: ")

    try:
        user = oerp.login(user, passwd, database)
    except ValueError, e:
        print "Wrong login ID or password"
        return False
    print(user.name)            # print the full name of the user
    print(user.company_id.name)
    return oerp



if __name__ == '__main__':
    connection = None
    try:
        connection = oerplib.OERP(server='localhost', protocol='xmlrpc', port=8069)
    except:
        raise "Not able to connect, please check connetion parameters!!!"
    while 1:
        db_name = show_db(connection)
        oerp = connect_db(connection, db_name)
        update_module(oerp)
