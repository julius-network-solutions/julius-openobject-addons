# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, api, _ 

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    _defaults = {
        'product_id': False,
    }

    @api.one
    @api.returns('product.product')
    def _create_employee_product(self):
        product = False
        product_obj = self.env['product.product']
        uom = self.env.ref('product.product_uom_hour')
        category = self.env.ref('hr_employee_product_auto.product_employee')
        taxes_id = [x.id for x in category.sale_taxes_ids]
        supplier_taxes_id = [x.id for x in category.purchase_taxes_ids]
        name = self.name or ''
        vals = {
                'name': name,
                'uom_id': uom and uom.id or False,
                'uom_po_id': uom and uom.id or False,
                'categ_id': category and category.id or False,
                'taxes_id': [(6,0, taxes_id)],
                'supplier_taxes_id': [(6,0, supplier_taxes_id)],
                'type': 'service',
                'standard_price': 1,
                'list_price': 1,
                }
        return product_obj.create(vals)

    @api.multi
    def create_employee_product(self):
        for employee in self:
            if not employee.product_id:
                product = self._create_employee_product()
                if product:
                    employee.product_id = product

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
