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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _


class product_product_costs(models.Model):
    _name = 'product.product.costs'
    _description = 'Product variant costs'
    _order = 'sequence'

    name = fields.Char(related='type_id.name', readonly=True, store=True)
    sequence = fields.Integer(required=True)
    type_id = fields.Many2one('product.costs.type', 'Cost type',
                              required=True)
    type = fields.Selection([
                             ('fixed', 'Fixed price'),
                             ('bom', 'BoM'),
                             ('bom_routing', 'BoM Routing'),
                             ('python', 'Python Computation'),
                             ('formula', 'Formula'),
                             ], related='type_id.type', readonly=True,
                            store=True)
    value = fields.Float('Value')
    product_id = fields.Many2one('product.product', 'Product',
                                 required=True, ondelete='cascade')

    @api.onchange('type_id')
    def onchange_type_id(self):
        if self.type_id.type == 'fixed':
            self.value = self.type_id.default_value


class product_product(models.Model):
    _inherit = 'product.product'

    costs_structure_id = fields.Many2one('product.costs.structure',
                                        'Cost structure')
    costs_line_ids = fields.One2many('product.product.costs', 'product_id',
                                     'Costs')

    @api.onchange('costs_structure_id')
    def onchange_cost_structure_id(self):
        self.costs_line_ids = False
        lines = []
        formula_lines = self.env['product.costs.structure.line']
        for line in self.costs_structure_id.line_ids:
            value = 0
            if line.type == 'fixed':
                value = line.default_value
            elif line.type == 'formula':
                formula_lines += line
                continue
            else:
                value = 10
            line_vals = {
                         'type_id': line.type_id.id,
                         'sequence': line.sequence,
                         'value': value,
                         }
            lines.append(line_vals)
        for line in formula_lines:
            value = sum(l['value'] for l in lines
                        if l['type_id'] in line.type_id.formula_ids.ids)
            line_vals = {
                         'type_id': line.type_id.id,
                         'sequence': line.sequence,
                         'value': value,
                         }
            lines.append(line_vals)
        self.costs_line_ids = lines

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
