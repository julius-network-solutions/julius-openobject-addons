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


class mrp_bom_update(models.TransientModel):
    _name = "mrp.bom.update"

    name = fields.Char('name')
    source_id = fields.Many2one('product.product', 'Source')
    target_id = fields.Many2one('product.product', 'Target')

    @api.one
    def button_update_bom(self):
        source = self.source_id
        target = self.target_id
        
        bom_lines = self.env['mrp.bom.line'].search([('product_id','=', source.id)])
        if target:
            bom_lines.write({'product_id': target.id})
        else:
            bom_lines.unlink()
        return {'type': 'ir.actions.act_window_close'}        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
