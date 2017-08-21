# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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

import datetime
from openerp import models, api, fields, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp


class product_revision_generator(models.TransientModel):
    _name = 'product.revision.generator'
    _description = 'Product revision generator'

    name = fields.Char('New revision index', required=True)
    product_id = fields.Many2one('product.product', 'Product',
                                 required=True, ondelete='cascade')
    origin_bom_id = fields.Many2one('mrp.bom', 'Origin BoM')
    line_ids = fields.One2many('product.revision.generator.line',
                               'generator_id', 'Lines')
    date_start = fields.Date('Valid From', help="Validity of this revision.",
                             required=True, default=fields.Date.today())
    date_stop = fields.Date('Valid Until', help="Validity of this revision. " \
                            "Keep empty if it's always valid.")
    revision_note = fields.Text()

    @api.model
    def _copy_product(self, product, default=None):
        if default is None:
            default = {}
        default['product_tmpl_id'] = product.product_tmpl_id.id
        return product.copy(default=default)

    @api.model
    def _write_product(self, product, vals=None):
        if vals is None:
            vals = {}
        vals.update({'state': 'obsolete', 'active': False})
        return product.write(vals)

    @api.multi
    def generate_index(self):
        self.ensure_one()
        product_obj = self.env['product.product']
        bom_obj = self.env['mrp.bom']
        bom_line_obj = self.env['mrp.bom.line']
        defaults = {}
        product = self.product_id
        revision_index = self.name
        date_start = self.date_start
        revision_note = self.revision_note
        date_stop = self.date_stop
        defaults.update({
                         'name': product.name,
                         'revision_index': revision_index,
                         'date_start': date_start,
                         'date_stop': date_stop,
                         'revision_note': revision_note,
                         'default_code': product.default_code,
                         'bom_ids': [],
                         })
        new_product = self.with_context(variant=True).\
            _copy_product(product, default=defaults)
        start = datetime.datetime.strptime(date_start, DF)
        date_stop_2 = (start + datetime.timedelta(days=-1)).strftime(DF)
        vals = {'date_stop': date_stop_2}
        self.with_context(variant=True)._write_product(product, vals)
        if self.origin_bom_id:
            new_bom = self.origin_bom_id.\
                copy(default={
                              'bom_line_ids': [],
                              'product_id': new_product.id,
                              })
            for line in self.line_ids:
                list_line_vals = line.copy_data()
                line_vals = list_line_vals and list_line_vals[0] or {}
                line_vals.pop('generator_id', None)
                line_vals.update({
                                  'bom_id': new_bom.id,
                                  })
                bom_line_obj.create(line_vals)
        try:
            action = self.env.ref('product.product_template_action')
        except ValueError:
            return False
        action = action.read()[0]
        views = action.get('views', [])
        new_order = [(False, u'form')]
        for view_id, mode in views:
            if mode == 'form':
                if view_id:
                    new_order[0][0] = view_id
            else:
                new_order.append((view_id, mode))
        action.update({
                       'res_id': new_product.product_tmpl_id.id,
                       'views': new_order,
                       'view_id': False,
                       })
        return action


class product_revision_generator_line(models.TransientModel):
    _name = 'product.revision.generator.line'
    _description = 'Product revision generator lines'

    generator_id = fields.Many2one('product.revision.generator',
                                   'Generator', required=True,
                                   ondelete='cascade')

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Product Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure',
        oldname='product_uom', required=True,
        help="Unit of Measure (Unit of Measure) is the unit of "
        "measurement for the inventory control")
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")
    attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Variants',
        help="BOM Product Variants needed form apply this line.")
    operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Consumed in Operation',
        help="The operation where the components are consumed, or "
        "the finished products created.")

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        if self.product_id:
            self.name = self.product_id.name
            self.product_uom = self.product_id.uom_id.id

    @api.onchange('product_uom_id')
    def onchange_uom(self):
        if self.product_uom_id.category_id.id != \
                self.product_id.uom_id.category_id.id:
            self.product_uom_id = self.product_id.uom_id.id
            return {
                    'warning': {
                                'title': _('Warning !'),
                                'message' : _('The Product Unit of Measure '
                                              'you chose has a different '
                                              'category than in the '
                                              'product form.'),
                                }
                    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
