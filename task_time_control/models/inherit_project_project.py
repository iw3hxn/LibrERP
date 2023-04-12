# -*- coding: utf-8 -*-
##############################################################################

from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import orm, fields


class ProjectProject(orm.Model):
    _inherit = "project.project"

    def create(self, cr, uid, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if context.get('no_create', False):
            raise orm.except_orm(
                'Errore',
                _('It is not allowed to create project from here'))
        return super(ProjectProject, self).create(cr, uid, values, context)
