# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

from openerp import api, models, fields

class operation_cycle(models.Model):
    _inherit = 'operation.cycle'
    
    task_id = fields.Many2one('project.task', 'Task')
            
class project_task(models.Model):
    _inherit = 'project.task'
    
    cycle_ids = fields.One2many('operation.cycle','task_id',string='Operation Cycles')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: