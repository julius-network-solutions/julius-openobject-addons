# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

#confirm_form = """<form string="Compute offered">
#    <separator colspan="4" string="Compute offered products for this sale" />
#    <label colspan="4" string="This will add a line with an offered product for each sale line that matches offered rules of its product." />
#    <label colspan="4" string="Important: please note that existing offered product lines will be removed." />
#</form>"""
#
#wrong_state_form = """<form string="Compute offered">
#    <label colspan="4" string="This only applies to sale orders in 'Draft' state." />
#</form>
#"""
class product_compute_offered(orm.TransientModel):
    _name = "product.compute.offered"    

    def do_compute_offered(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        o_so = self.pool.get('sale.order')
        sale_ids = o_so.search(cr, uid, [('state', '=', 'draft')], context=context)
        o_so._generate_offered(cr, uid, sale_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

#    def check_sale_order_state(wiz, cr, uid, data, context):
#        so_id = data['ids'][0]
#        o_so = pooler.get_pool(cr.dbname).get('sale.order')
#        b_so = o_so.browse(cr, uid, so_id, context)
#        return b_so.state == 'draft' and 'ask_confirmation' or 'not_draft'
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
