# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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

from datetime import datetime as DT
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp import models, fields, api


class hr_employee_experience(models.Model):
    _name = 'hr.employee.experience'
    _description = 'Experiences of my employees'
    _order = 'date_start DESC'

    name = fields.Char(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    duration = fields.Integer('Duration in Month', compute='_get_duration')
    city = fields.Char()
    description = fields.Html()
    employee_id = fields.Many2one('hr.employee', 'Employee/Applicant')

    @api.one
    def _get_duration(self):
        duration = 0
        if self.date_start or self.date_end:
            start = self.date_start
            end = self.date_end or fields.Date.today()
            if start < end:
                diff = relativedelta(DT.strptime(end, DF),
                                     DT.strptime(start, DF))
                duration = int(round(diff.years * 12 + \
                                     diff.months + diff.days / 31.0))
        self.duration = duration


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
