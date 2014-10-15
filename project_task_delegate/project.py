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

from openerp import models, fields, api, _

class project_task(models.Model):
    _inherit = "project.task"    

    global_planned_hours = fields.Float('Global Planned Hours',
                                        compute='_calc_global_hours',
                                        store=False)

    global_remaining_hours = fields.Float('Global Remaining Hours',
                                        compute='_calc_global_hours',
                                        store=False)

    @api.one
    @api.depends('planned_hours', 'remaining_hours', 'child_ids')
    def _calc_global_hours(self):
        planned_hours = 0.0
        remaining_hours = 0.0
        for child in self.child_ids:
            planned_hours += child.planned_hours
            remaining_hours += child.remaining_hours
        self.global_planned_hours = planned_hours
        self.global_remaining_hours = remaining_hours
    
    def do_delegate(self, cr, uid, ids, delegate_data=None, context=None):
        """
        Delegate Task to another users.
        """
        if delegate_data is None:
            delegate_data = {}
        assert delegate_data['user_id'], _("Delegated User should be specified")
        delegated_tasks = {}
        for task in self.browse(cr, uid, ids, context=context):
            delegated_task_id = self.copy(cr, uid, task.id, {
                'name': delegate_data['name'],
                'project_id': delegate_data['project_id'] and delegate_data['project_id'][0] or False,
                'user_id': delegate_data['user_id'] and delegate_data['user_id'][0] or False,
                'planned_hours': delegate_data['planned_hours'] or 0.0,
                'remaining_hours': delegate_data['planned_hours'] or 0.0,
                'parent_ids': [(6, 0, [task.id])],
                'description': delegate_data['new_task_description'] or '',
                'child_ids': [],
                'work_ids': []
            }, context=context)
            self._delegate_task_attachments(cr, uid, task.id, delegated_task_id, context=context)
            task.write({
                'remaining_hours': task.remaining_hours - delegate_data['planned_hours'],
                'planned_hours': task.planned_hours - delegate_data['planned_hours'],
            }, context=context)
            delegated_tasks[task.id] = delegated_task_id
        return delegated_tasks
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
