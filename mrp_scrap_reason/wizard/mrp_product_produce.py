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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api, _


class MRPProductProduceScrap(models.TransientModel):
    _name = "mrp.product.produce.scrap"
    _description = "Scrap product from production"
 
    @api.model
    def _scrap_reason_get(self):
        reasons = self.env['stock.move.scrap.reason'].search([])
        reasons = reasons.name_get()
        result = []
        for key, value in reasons:
            result.append((str(key), value))
        result.append(('-1', _('Other...')))
        return result
 
    wiz_id = fields.Many2one("mrp.product.produce", "Product production")
    product_qty = fields.Float("Quantity to scrap", default=0.0)
    product_id = fields.Many2one("product.product", "Product", required=True)
    reason = fields.Selection(_scrap_reason_get,
                              'Reason', help="Reason for scraping.")
    notes_reason = fields.Text('Notes')

    def _get_scrap_values(self):
        reason = str(self.reason)
        vals = {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'scrap_qty': self.product_qty,
                'reason': reason,
                'production_id': self.wiz_id.production_id.id,
                'location_id': self.wiz_id.production_id.move_raw_ids.
                filtered(lambda x: x.state not in ('done', 'cancel')) and \
                self.wiz_id.production_id.location_src_id.id or \
                self.wiz_id.production_id.location_dest_id.id,
                'origin': self.wiz_id.production_id.name,
                }
        if reason == '-1':
            vals.update({'notes_reason': self.notes_reason})
        return vals

    def scrap_componant(self):
        scraps = self.env['stock.scrap']
        for scrap in self:
            scrap_vals = scrap._get_scrap_values()
            scraps |= self.env['stock.scrap'].create(scrap_vals)
        return scraps


class MRPProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def default_get_scrap_values(self, product):
        return {
                'product_id': product.id,
                'product_qty': 0,
                'reason': False,
                'notes_reason': '',
                }

    @api.model
    def default_get_scrap_lines(self, production):
        scrap_ids = []
        boms, exploded_lines = production.bom_id.\
            explode(production.product_id, 1,
                    picking_type=production.bom_id.picking_type_id)
        for bom_line, line_data in exploded_lines:
            product = bom_line.product_id
            values = self.default_get_scrap_values(product)
            scrap_ids.append((0, 0, values))
        return scrap_ids

    @api.model
    def default_get(self, fields):
        res = super(MRPProductProduce, self).default_get(fields)
        active_model = self._context and self._context.get('active_model')
        production_id = self._context and self._context.get('active_id')
        production = self.env['mrp.production']
        if active_model == 'mrp.production':
            production = production.\
                browse(self._context['active_id'])
        if production:
            scrap_ids = self.default_get_scrap_lines(production)
            res.update({'scrap_ids': scrap_ids})
        return res

    scrap_ids = fields.One2many('mrp.product.produce.scrap',
                                'wiz_id', "Scrap components")

    @api.multi
    def do_produce(self):
        if self.product_qty:
            scraps = self.scrap_ids.filtered(lambda s: s.product_qty != 0)
            if scraps:
                scraps.scrap_componant()
        return super(MRPProductProduce, self).do_produce()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
