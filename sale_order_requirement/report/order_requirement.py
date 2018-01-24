# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################
#
#    To customize report layout :
#
#    1 - Configure final layout using bom_structure.sxw in OpenOffice
#    2 - Compile to bom_structure.rml using ..\base_report_designer\openerp_sxw2rml\openerp_sxw2rml.py
#           python openerp_sxw2rml.py bom_structure.sxw > bom_structure.rml
#
##############################################################################
import os
import time
from report import report_sxw
from operator import itemgetter
from tools.translate import _


def _moduleName():
    path = os.path.dirname(__file__)
    return os.path.basename(os.path.dirname(path))


openerpModule = _moduleName()


def _thisModule():
    return os.path.splitext(os.path.basename(__file__))[0]


thisModule = _thisModule()


def _translate(value):
    return _(value)


###############################################################################################################à

MODEL = 'order.requirement'
REPORTNAME = 'order.requirement.explosion'


def _createtemplate():
    """
        Automatic XML menu creation
    """
    filepath = os.path.dirname(__file__)
    fileName = thisModule + '.xml'
    fileOut = open(os.path.join(filepath, fileName), 'w')

    listout = [[MODEL, 'order_requirement_report', 'Order Requirement', REPORTNAME]]

    fileOut.write(u'<?xml version="1.0"?>\n<openerp>\n    <data>\n\n')
    fileOut.write(u'<!--\n       IMPORTANT : DO NOT CHANGE THIS FILE, IT WILL BE REGENERERATED AUTOMATICALLY\n-->\n\n')

    for model, label, description, name in listout:
        fileOut.write(
            u'        <report auto="True"\n                header="True"\n                model="%s"\n' % (model))
        fileOut.write(u'                id="%s"\n                string="%s"\n                name="%s"\n' % (
        label, description, name))
        fileOut.write(u'                rml="%s/report/%s.rml"\n' % (openerpModule, thisModule))
        fileOut.write(u'                report_type="pdf"\n                file=""\n                 />\n')

    fileOut.write(u'<!--\n       IMPORTANT : DO NOT CHANGE THIS FILE, IT WILL BE REGENERERATED AUTOMATICALLY\n-->\n\n')
    fileOut.write(u'    </data>\n</openerp>\n')
    fileOut.close()


_createtemplate()


###############################################################################################################à


class order_requirement_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order_requirement_report, self).__init__(cr, uid, name, context=context)
        # self.localcontext.update({
        #     'get_order': self.get_order,
        #     'get_operations': self.get_operations,
        #     'get_children': self.get_children,
        # })


report_sxw.report_sxw('report.' + REPORTNAME, MODEL, '/' + openerpModule + '/report/' + thisModule + '.rml',
                      parser=order_requirement_report, header='internal')
