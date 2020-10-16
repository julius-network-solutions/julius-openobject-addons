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

from operator import mul, div, sub
import time
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval


class product_product_costs(models.Model):
    _name = 'product.product.costs'
    _description = 'Product variant costs'
    _order = 'sequence'

    name = fields.Char(related='type_id.name', readonly=True, store=True)
    sequence = fields.Integer(required=True, default=1)
    type_id = fields.Many2one('product.costs.type', 'Cost type',
                              required=True)
    type = fields.Selection([
                             ('fixed', 'Fixed price'),
                             ('bom', 'BoM'),
                             ('bom_routing', 'BoM Routing'),
                             ('python', 'Python Computation'),
                             ('field', 'Linked Field'),
                             ('formula', 'Formula'),
                             ], related='type_id.type', readonly=True,
                            store=True)
    formula_type = fields.Selection([
                                     ('sum', 'Sum'),
                                     ('subtraction', 'Subtraction'),
                                     ('multiplication', 'Multiplication'),
                                     ('division', 'Division'),
                                     ], related='type_id.formula_type',
                                    readonly=True, store=True)
    value = fields.Float('Value', digits=dp.get_precision('Product Price'))
    product_id = fields.Many2one('product.product', 'Product',
                                 required=True, ondelete='cascade')
    can_update_product_price = fields.\
        Boolean(related='type_id.can_update_product_price',
                readonly=True, store=True)

    @api.onchange('type_id')
    def onchange_type_id(self):
        if self.type_id.type == 'fixed':
            self.value = self.type_id.default_value

    @api.one
    def update_standard_price(self):
        """
        This method will put the selected value to
        the standard price of the selected product.
        """
        if self.product_id.cost_method == 'standard':
            self.product_id.standard_price = self.value
            self.product_id.date_update_standard_price = datetime.now()
        return True

    @api.multi
    def get_formula_value(self):
        """
        This method will recompute the value from the other lines
        """
        self.ensure_one()
        value = 0
        lines = self.search([('product_id', '=', self.product_id.id)])
        formula_values = [l.value for l in lines if l.type_id.id
                          in self.type_id.formula_ids.ids]
        if formula_values:
            if self.formula_type == 'sum':
                value = sum(formula_values)
            elif self.formula_type == 'subtraction':
                value = reduce(sub, formula_values)
            elif self.formula_type == 'multiplication':
                value = reduce(mul, formula_values)
            elif self.formula_type == 'division':
                value = reduce(div, formula_values)
        return value

    @api.one
    def update_formula_value(self):
        """
        This method will update the value from the other lines
        """
        if self.type == 'formula':
            self.value = self.get_formula_value()

    @api.one
    def update_line_value(self):
        """
        This method will update the value for this lines
        """
        product = self.product_id
        if self.type not in ('fixed', 'formula'):
            value = 0
            if self.type == 'bom':
                value = product._get_bom_price(cost_type_id=self.type_id.id)[0]
            elif self.type == 'bom_routing':
                value = product._get_bom_routing_price()[0]
            elif self.type == 'field':
                value = product._get_field_price(expr=self.type_id.field_expr)[0]
            elif self.type == 'python':
                value = product.\
                    _get_python_price(expr=self.type_id.python_code)[0]
            self.value = value


class product_product(models.Model):
    _inherit = 'product.product'

    costs_structure_id = fields.Many2one('product.costs.structure',
                                        'Cost structure')
    costs_line_ids = fields.One2many('product.product.costs', 'product_id',
                                     'Costs')
    bom_cost_type_id = fields.Many2one('product.costs.type',
                                       'BoM default cost type',
                                       help='If filed, when the product will '
                                       'be selected in a BoM line, this value '
                                       'will be set by default.',
                                       domain=[('type', '=', 'bom')])
    date_update_standard_price = fields.Date('Last Update')
    
    @api.one
    def _get_bom_price(self, cost_type_id=None):
        """
        Get purchase price of related BoMs
        """
        total = 0
        product_obj = self.env['product.product']
        uom_obj = self.env['product.uom']
        bom = self.bom_ids and self.bom_ids[0]
        factor = bom.product_uom.factor / self.uom_id.factor
        sub_boms = bom.\
            _bom_explode_cost(bom=bom, product=self,
                              factor=factor / (bom.product_qty or 0.0001))
        def process_bom(bom_dict, factor=1):
            sum_strd = 0
            prod = product_obj.browse(bom_dict['product_id'])
            prod_qty = factor * bom_dict['product_qty']
            product_uom = uom_obj.browse(bom_dict['product_uom'])
            std_price = uom_obj._compute_price(from_uom_id=prod.uom_id.id,
                                               price=prod.standard_price,
                                               to_uom_id=product_uom.id)
            sum_strd = prod_qty * std_price
            return sum_strd
        parent_bom = {
                      'product_qty': bom.product_qty,
                      'product_uom': bom.product_uom.id,
                      'product_id': bom.product_id.id,
                      }
        for sub_bom in (sub_boms and sub_boms[0]) or [parent_bom]:
            if cost_type_id and sub_bom.get('cost_type_id') and \
                    sub_bom['cost_type_id'] == cost_type_id:
                total += process_bom(sub_bom)
        return total

    @api.one
    def _get_bom_routing_price(self):
        """
        Get routing price of related BoMs
        """
        total = 0
        product_obj = self.env['product.product']
        uom_obj = self.env['product.uom']
        workcenter_obj = self.env['mrp.workcenter']
        routing_workcenter_obj = self.env['mrp.routing.workcenter']
        bom = self.bom_ids and self.bom_ids[0]
        factor = self.uom_id.factor / bom.product_uom.factor
        sub_boms = bom._bom_explode(bom=bom, product=self,
                                    factor=factor / bom.product_qty)
        def process_workcenter(wrk):
            workcenter = workcenter_obj.browse(wrk['workcenter_id'])
            cost_cycle = wrk['cycle'] * workcenter.costs_cycle
            cost_hour = wrk['hour'] * workcenter.costs_hour
            total = cost_cycle + cost_hour
            wc_use = routing_workcenter_obj.browse(wrk['wc_use'])
            effective = wc_use.effective or 1
            total *= effective
            total += (wc_use.prepare_time * effective *
                      workcenter.costs_hour * wrk['cycle'] / wc_use.nbr_pcs)
            return total
        for wrk in (sub_boms and sub_boms[1]):
            total += process_workcenter(wrk)
        return total

    @api.one
    def _get_field_price(self, expr=''):
        """
        Get price from a related field
        """
        value = 0
        user = self.env['res.users'].browse(self._uid)
        space = {
                'self': self,
                'product': self,
                'cr': self._cr,
                'uid': self._uid,
                'user': user,
                'time': time,
                # copy context to prevent side-effects of eval
                'context': self._context.copy()}
        try:
            value = safe_eval(expr,
                              space)
            value = value and float(value) or 0
        except Exception, e:
            _logger.warning('Error on the computation: %s', e)
            pass
        return value

    @api.one
    def _get_python_price(self, expr=''):
        """
        Get price from a python expression
        """
        value = 0
        user = self.env['res.users'].browse(self._uid)
        space = {
                'self': self,
                'product': self,
                'cr': self._cr,
                'uid': self._uid,
                'user': user,
                'time': time,
                # copy context to prevent side-effects of eval
                'context': self._context.copy()}
        try:
            safe_eval(expr, space, mode='exec', nocopy=True)
            value = space and space.get('result') and \
                float(space['result']) or 0
        except Exception, e:
            _logger.warning('Error on the computation: %s', e)
            pass
        return value

    @api.one
    def _get_cost_lines(self, onchange=False):
        """
        This method will update the costs lines of the selected product
        """
        lines = []
        formula_lines = self.env['product.costs.structure.line']
        for line in self.costs_structure_id.line_ids:
            value = 0
            if line.type == 'fixed':
                value = line.default_value
            elif onchange:
                if line.type == 'formula':
                    formula_lines += line
                    continue
                elif line.type == 'bom':
                    value = self._get_bom_price(cost_type_id=line.type_id.id)[0]
                elif line.type == 'bom_routing':
                    value = self._get_bom_routing_price()[0]
                elif line.type == 'field':
                    value = self._get_field_price(expr=line.type_id.field_expr)[0]
                elif line.type == 'python':
                    value = self.\
                        _get_python_price(expr=line.type_id.python_code)[0]
            line_vals = {
                         'type_id': line.type_id.id,
                         'sequence': line.sequence,
                         'value': value,
                         }
            lines.append(line_vals)
        if onchange:
            for line in formula_lines:
                value = 0
                formula_values = [l['value'] for l in lines if l['type_id']
                                  in line.type_id.formula_ids.ids]
                if formula_values:
                    if line.formula_type == 'sum':
                        value = sum(formula_values)
                    elif line.formula_type == 'subtraction':
                        value = reduce(sub, formula_values)
                    elif line.formula_type == 'multiplication':
                        value = reduce(mul, formula_values)
                    elif line.formula_type == 'division':
                        value = reduce(div, formula_values)
                line_vals = {
                             'type_id': line.type_id.id,
                             'sequence': line.sequence,
                             'value': value,
                             }
                lines.append(line_vals)
        return lines

    @api.one
    @api.onchange('costs_structure_id')
    def onchange_cost_structure_id(self):
        self.costs_line_ids = False
        for new_lines in self._get_cost_lines(onchange=True):
            self.costs_line_ids = new_lines

    @api.one
    def update_cost_lines(self):
        for new_lines in self._get_cost_lines():
            self.costs_line_ids.unlink()
            costs_lines = [(0, 0, line) for line in new_lines]
            self.costs_line_ids = costs_lines
        self.update_line_values()
        return True

    @api.one
    def update_line_values(self):
        cost_lines = self.env['product.product.costs'].\
            search([
                    ('product_id', '=', self.id),
                    ('type', 'not in', ('fixed', 'formula')),
                    ])
        cost_lines.update_line_value()
        formula_lines = self.env['product.product.costs'].\
            search([
                    ('product_id', '=', self.id),
                    ('type', '=', 'formula'),
                    ])
        formula_lines.update_formula_value()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
