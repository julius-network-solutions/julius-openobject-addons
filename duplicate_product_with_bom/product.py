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

from openerp import models, fields, api

class product_template(models.Model):
    _inherit = "product.template"
    @api.one
    def copy_product(self):
        @api.returns('product.template')
        def afun(self,x):
            print x,
            return x

        p = []
        for attribute in self.attribute_line_ids:
            values = {
                    'attribute_id':attribute.attribute_id.id,
                    'value_ids':[(6,0 ,attribute.value_ids.ids)],
                      }
            p.append((0, 0, values))

        boms = self.env['mrp.bom'].search([('product_tmpl_id', 'in', self.ids)])
        bom_copies = boms.copy(default=None)
        new_product = self.copy()
        bom_copies.write({'product_tmpl_id':new_product.id})
        new_product.write({'attribute_line_ids':p})

        return afun(self, new_product.id)

