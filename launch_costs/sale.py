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
        'launch_costs' : fields.float('Launch Costs'),
        'launch_costs_line_id': fields.many2one('account.invoice.line', 'Launch Costs invoice line'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default['launch_costs_line_id'] = False
        return super(sale_order_line, self).copy(cr, uid, id, default, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default['launch_costs_line_id'] = False
        return super(sale_order_line, self).copy_data(cr, uid, id, default, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: