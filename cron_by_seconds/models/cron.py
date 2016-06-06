# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Julius Network Solutions SARL <contact@julius.fr>
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

import openerp
from openerp import models, fields

from dateutil.relativedelta import relativedelta


openerp.addons.base.ir.ir_cron._intervalTypes.\
    update({
            'seconds': lambda interval: relativedelta(seconds=interval),
            })

class ir_cron(models.Model):
    _inherit = 'ir.cron'

    interval_type = fields.Selection(selection_add=[('seconds', 'Seconds')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
