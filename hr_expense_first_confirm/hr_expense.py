# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, orm
from openerp import tools
from tools import DEFAULT_SERVER_DATE_FORMAT
from tools.translate import _
from tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp


class hr_expense_expense(orm.Model):
    _inherit = 'hr.expense.expense'
    
    def first_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'confirmed': True}, context=context)
        return True
    
    def unconfirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'confirmed': False}, context=context)
        return True
    
    _columns = {
        'confirmed': fields.boolean('Confirmed'),
    }


    _defaults = {
        'confirmed': False,
    }