#!/usr/bin/env python

import time
import xmlrpclib


class OpenErpRpc60(object):
    """
    https://doc.odoo.com/6.0/developer/6_22_XML-RPC_web_services/
    """
    def __init__(self, config):
        # server proxy object
        xmlrpc_common = xmlrpclib.ServerProxy(config.XMLRPC_SERVER + 'common')
        self.uid = xmlrpc_common.login(config.ERP_DB, config.ERP_USER, config.ERP_PASS)
        self.xmlrpc_object = xmlrpclib.ServerProxy(config.XMLRPC_SERVER + 'object')

        self.password = config.ERP_PASS
        self.db_name = config.ERP_DB

        self.xmlrpc_report = xmlrpclib.ServerProxy(config.XMLRPC_SERVER + 'report')

    # helper function for invoking model methods
    def execute(self, model, method, args, fields=None):
        if method == 'search_read':
            row_ids = self.execute(model, 'search', args)
            return self.execute(model, 'read', row_ids, fields=fields)

        if fields:
            return self.xmlrpc_object.execute(self.db_name, self.uid, self.password, model, method, args, fields)
        else:
            return self.xmlrpc_object.execute(self.db_name, self.uid, self.password, model, method, args)

    def report(self, model_name, ids, args):
        return self.xmlrpc_report.report(self.db_name, self.uid, self.password, model_name, ids, args)

    def report_get(self, report_id):
        report = self.xmlrpc_report.report_get(self.db_name, self.uid, self.password, report_id)
        if report.get('result'):
            return report
        else:
            time.sleep(1)
            return self.xmlrpc_report.report_get(self.db_name, self.uid, self.password, report_id)

    def get_report(self, model_name, ids, args):
        report_id = self.report(model_name, ids, args)
        return self.report_get(report_id)


if __name__ == "__main__":
    from config_rpc import config

    import os

    rpc = OpenErpRpc60(config)

    companies = rpc.execute('res.company', 'search_read', [], ('order_import_path', ))
    dir_path = companies[0]['order_import_path']
    for file_name in os.listdir(dir_path):
        if file_name[-3:] == 'xml':
            file_path = os.path.join(dir_path, file_name)
            os.chmod(file_path, 0664)

    rpc.execute('sale.order', 'load_orders', False)
