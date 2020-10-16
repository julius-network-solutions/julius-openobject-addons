# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import fields, models, _


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    wanted_date = fields.Date()


class sale_order(models.Model):
    _inherit = "sale.order"

    def _get_date_planned(self, cr, uid, order,
                          line, start_date, context=None):
        result = super(sale_order, self).\
            _get_date_planned(cr, uid, order, line, start_date, context=None)
        if line.wanted_date:
            result = line.wanted_date
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
