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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.safe_eval import safe_eval as eval

class product_revision_generator(orm.TransientModel):
    _name = 'product.revision.generator'
    _description = 'Product revision generator'

    _columns = {
        'name': fields.char('New revision index', required=True),
        'product_id': fields.many2one('product.product',
                                      'Product', required=True),
        'origin_bom_id': fields.many2one('mrp.bom', 'Origin BoM'),
        'line_ids': fields.one2many('product.revision.generator.line',
                                    'generator_id', 'Lines'),
        'date_start': fields.date('Valid From',
                                  help="Validity of this revision.",
                                  required=True),
        'date_stop': fields.date('Valid Until',
                                 help="Validity of this revision. " \
                                 "Keep empty if it's always valid."),
        'revision_note': fields.text('Revision note'),
    }

    _defaults = {
        'date_start': fields.date.context_today,
    }

    def _copy_product(self, cr, uid, product_id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        product_obj = self.pool.get('product.product')
        vals = product_obj.copy_data(cr, uid, product_id,
                                     default=default, context=context)
        if default.get('name'):
            vals['name'] = default['name']
        if default.get('default_code'):
            vals['default_code'] = default['default_code']
        return product_obj.create(cr, uid, vals, context=context)

    def _write_product(self, cr, uid, product_id, vals=None, context=None):
        if context is None:
            context = {}
        if vals is None:
            vals = {}
        product_obj = self.pool.get('product.product')
        return product_obj.write(cr, uid, product_id, vals, context=context)

    def generate_index(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        bom_obj = self.pool.get('mrp.bom')
        defaults = {}
        rec = self.browse(cr, uid, ids[0], context=context)
        product = rec.product_id
        revision_index = rec.name
        date_start = rec.date_start
        revision_note = rec.revision_note or ''
        date_stop = rec.date_stop or False
        defaults.update({
            'product_tmpl_id': product.product_tmpl_id.id,
            'name': product.name,
            'revision_index': revision_index,
            'date_start': date_start,
            'date_stop': date_stop,
            'revision_note': revision_note,
            'default_code': product.default_code or '',
            'bom_ids': [],
        })
        new_product_id = self._copy_product(cr, uid, product.id,
                                            default=defaults, context=context)
        start = datetime.datetime.strptime(date_start, DF)
        date_stop_2 = (start + datetime.timedelta(days=-1)).strftime(DF)
        vals = {'date_stop': date_stop_2}
        self._write_product(cr, uid, product.id, vals, context=context)
        if rec.origin_bom_id:
            new_bom_id = bom_obj.\
                copy(cr, uid, rec.origin_bom_id.id,
                     default={'bom_lines': [], 'product_id': new_product_id},
                     context=context)
            for line in rec.line_ids:
                line_vals = {
                    'name': line.name,
                    'code': line.code,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'company_id': line.company_id and \
                        line.company_id.id or False,
                    'sequence': line.sequence,
                    'bom_id': new_bom_id,
                }
                bom_obj.create(cr, uid, line_vals, context=context)
        data_obj = self.pool.get('ir.model.data')
        action_obj = self.pool.get('ir.actions.act_window')
        try:
            model, res_id = data_obj.\
                get_object_reference(cr, uid, 'product',
                                     'product_normal_action')
        except:
            return True
        action = action_obj.read(cr, uid, res_id, context=context)
        action.update({'res_id': new_product_id})
        views = action.get('views', [])
        new_order = [(False, u'form')]
        for view_id, mode in views:
            if mode == 'form':
                if view_id:
                    new_order[0][0] = view_id
            else:
                new_order.append((view_id,mode))
        action['res_id'] = new_product_id
        action['views'] = new_order
        action['view_id'] = False
        return action

class product_revision_generator_line(orm.TransientModel):
    _name = 'product.revision.generator.line'
    _description = 'Product revision generator lines'

    _columns = {
        'generator_id': fields.many2one('product.revision.generator',
                                        'Generator', required=True),
        'name': fields.char('Name', size=64),
        'code': fields.char('Reference', size=16),
        'product_id': fields.many2one('product.product', 'Product',
                                      required=True),
        'product_uos_qty': fields.float('Product UOS Qty'),
        'product_uos': fields.many2one('product.uom', 'Product UOS',
                                       help="Product UOS (Unit of Sale) is " \
                                       "the unit of measurement for the " \
                                       "invoicing and promotion of stock."),
        'product_qty': fields.float('Product Quantity', required=True,
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom': fields.many2one('product.uom',
                                       'Product Unit of Measure',
                                       required=True,
                                       help="Unit of Measure (Unit of" \
                                       " Measure) is the unit of measurement" \
                                       " for the inventory control"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'sequence': fields.integer('Sequence',
                                   help="Gives the sequence order when " \
                                   "displaying a list of bills of material."),
    }

    def onchange_product_id(self, cr, uid, ids,
                            product_id, name, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        if product_id:
            prod = self.pool.get('product.product').\
                browse(cr, uid, product_id, context=context)
            return {'value': {'name': prod.name,
                              'product_uom': prod.uom_id.id}}
        return {}

    def onchange_uom(self, cr, uid, ids,
                     product_id, product_uom, context=None):
        res = {'value':{}}
        if not product_uom or not product_id:
            return res
        product = self.pool.get('product.product').\
            browse(cr, uid, product_id, context=context)
        uom = self.pool.get('product.uom').\
            browse(cr, uid, product_uom, context=context)
        if uom.category_id.id != product.uom_id.category_id.id:
            res['warning'] = {'title': _('Warning'),
                              'message': _('The Product Unit of Measure ' \
                                           'you chose has a different ' \
                                           'category than in the ' \
                                           'product form.')}
            res['value'].update({'product_uom': product.uom_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
