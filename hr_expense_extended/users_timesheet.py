# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from report.interface import toxml
import pooler
import hr_timesheet.report.users_timesheet


# Monkeypatching:
def emp_create_xml(cr, uid, som, eom, emp):
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
    max_work_hours = user.company_id.timesheet_max_difference

    # Computing the attendence by analytical account
    cr.execute(
        """select line.date, (unit_amount / unit.factor) as amount
        from account_analytic_line as line, hr_analytic_timesheet as hr,
        product_uom as unit
        where hr.line_id=line.id
        and product_uom_id = unit.id
        and line.user_id=%s and line.date >= %s and line.date < %s
        order by line.date""",
        (uid, som.strftime('%Y-%m-%d'), eom.strftime('%Y-%m-%d')))

    # Sum by day
    month = {}
    for presence in cr.dictfetchall():
        day = int(presence['date'][-2:])
        month[day] = month.get(day, 0.0) + presence['amount']
        if month[day] > max_work_hours:
            month[day] = max_work_hours

    xml = '''
    <time-element date="%s">
        <amount>%.2f</amount>
    </time-element>
    '''
    time_xml = ([xml % (day, amount) for day, amount in month.iteritems()])

    # Computing the xml
    xml = '''
    <employee id="%d" name="%s">
    %s
    </employee>
    ''' % (uid, toxml(emp), '\n'.join(time_xml))
    return xml

hr_timesheet.report.users_timesheet.emp_create_xml = emp_create_xml
