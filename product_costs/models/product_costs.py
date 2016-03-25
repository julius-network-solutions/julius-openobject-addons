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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class product_costs_type(models.Model):
    _name = 'product.costs.type'
    _description = 'Product costs type'
    _order = 'sequence'

    name = fields.Char(required=True)
    type = fields.Selection([
                             ('fixed', 'Fixed price'),
                             ('bom', 'BoM'),
                             ('bom_routing', 'BoM Routing'),
                             ('python', 'Python Computation'),
                             ('formula', 'Formula'),
                             ], default='fixed', required=True)
    default_value = fields.Float(digits=dp.get_precision('Product Price'))
    python_code = fields.Text()
    formula_ids = fields.Many2many('product.costs.type',
                                   'product_costs_type_formula_rel',
                                   'product_costs_id', 'linked_costs_id',
                                   'Formulas',
                                   help="When formula is selected, the value "
                                   "will be computed by summing the value of "
                                   "linked costs")
    sequence = fields.Integer(required=True, default=1)


class product_costs_structure(models.Model):
    _name = 'product.costs.structure'
    _description = 'Product costs structure'

    name = fields.Char(required=True)
    line_ids = fields.One2many('product.costs.structure.line', 'structure_id',
                               'Lines')


class product_costs_structure_line(models.Model):
    _name = 'product.costs.structure.line'
    _description = 'Product costs structure line'
    _order = 'sequence'

    name = fields.Char(related='type_id.name', readonly=True, store=True)
    type_id = fields.Many2one('product.costs.type', 'Cost type',
                              required=True)
    default_value = fields.Float('Default value',
                                 digits=dp.get_precision('Product Price'))
    structure_id = fields.Many2one('product.costs.structure', 'Structure',
                                   required=True, ondelete='cascade')
    sequence = fields.Integer(required=True, default=1)
    type = fields.Selection([
                             ('fixed', 'Fixed price'),
                             ('bom', 'BoM'),
                             ('bom_routing', 'BoM Routing'),
                             ('python', 'Python Computation'),
                             ('formula', 'Formula'),
                             ], related='type_id.type', readonly=True,
                            store=True)

    @api.onchange('type_id')
    def onchange_type_id(self):
        self.sequence = self.type_id.sequence or 1
        self.default_value = self.type_id.default_value or 1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
