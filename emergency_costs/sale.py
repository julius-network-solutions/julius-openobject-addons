# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'emergency_costs' : fields.float('Emergency Costs'),
        'emergency_costs_generated' : fields.boolean('Emergency Costs Generated', readonly=True),
    }
    
    _defaults = {
        'emergency_costs_generated' : False,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: