# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-Today Julius Network Solutions SARL <contact@julius.fr>
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

from datetime import datetime, timedelta

from openerp import models, fields, api


class project_issue(models.Model):
    _inherit = "project.issue"

    @api.multi
    def create_task_work_from_issue(self):
        self.ensure_one()
        action = self.env.\
            ref('project_task_work_calendar_view.action_view_task_work')
        action_read = action.read([])[0]
        now = fields.Datetime.now()
        start = fields.Datetime.from_string(now) + timedelta(hours=-1)
        if start.minute >= 45:
            minute = "45"
        elif start.minute >= 30:
            minute = "30"
        elif start.minute >= 15:
            minute = "15"
        elif start.minute < 15:
            minute = "00"
        date_format = "%Y-%m-%d %H:" + "%s:00" % minute
        start_formatted = start.strftime(date_format)
        context_action = self._context.copy()
        context_action.update({
                               "default_name": self.name,
                               "default_hours": 1,
                               "default_date": start_formatted,
                               })
        if self.project_id:
            context_action({
                            "domain_task": self.project_id.id,
                            })
        view_id = self.env.ref("project.view_task_work_form").id
        action_read.update({
                            "views": [
                                      (view_id, "form"),
                                      (False, "calendar"),
                                      (False, "tree"),
                                      ],
                            "view_mode": "form,calendar,tree",
                            "view_id": view_id,
                            "context": context_action,
                            })
        return action_read

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
