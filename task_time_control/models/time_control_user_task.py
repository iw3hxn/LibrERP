# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#    $Jesús Ventosinos Mayor$
#    $Javier Colmenero Fernández$
#    Copyright (c) 2014 Didotech srl (info at didotech.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class time_control_user_task(orm.Model):
    _name = 'time.control.user.task'
    _columns = {
        'user': fields.many2one('res.users', 'user'),
        'work_start': fields.datetime('Work start'),
        'work_end': fields.datetime('Work end'),
        'started_task': fields.many2one('project.task', 'Started task')
    }


