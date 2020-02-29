# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2019 Didotech SRL (https://www.didotech.com)
#
##############################################################################


from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


class ProjectIssueStatus(orm.Model):

    _name = 'project.issue.status'

    _columns = {
        'name': fields.char(string='Status Name', size=30, required=True, help='Status codename, should be unique'),
        'description': fields.text(string='Status Description', required=False, help='Detailed explanation of the meaning of the status'),
    }

    # TODO: Add constraint to ensure uniqueness of 'name' field
    _sql_constraints = [
        # Fields of tuple:
        # (<constraint name used on DB server>, <SQL query that enforces the constraint>, <Error message to be shown to the user>)
        ('project_issue_status_name_uniq', 'unique(name)', 'Status name must be unique!')
    ]

# end project_issue_status