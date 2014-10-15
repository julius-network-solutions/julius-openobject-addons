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
    
class project_task_delegate(models.TransientModel):
    _inherit = "project.task.delegate"    

    name = fields.Char(size=128)

    @api.model
    def default_get(self, fields_list):
        """
        This function gets default values
        """
        res = super(project_task_delegate, self).default_get(fields_list)
        context = self._context
        active_id = context.get('active_id')
        model = 'project.task'
        active_model = context.get('active_model')
        if not active_id or active_model != model:
            return res
        task = self.env[model].browse(active_id)
        if 'project_id' in fields_list:
            res['project_id'] = task.project_id.id
        if 'name' in fields_list:
            res['name'] = (task.name or '') + _(': Delegated')
        if 'planned_hours' in fields_list:
            res['planned_hours'] = 1.0
        if 'new_task_description' in fields_list:
            res['new_task_description'] = task.description
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
