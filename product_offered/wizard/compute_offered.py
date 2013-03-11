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

import wizard
import netsvc
import pooler
confirm_form = """<form string="Compute offered">
    <separator colspan="4" string="Compute offered products for this sale" />
    <label colspan="4" string="This will add a line with an offered product for each sale line that matches offered rules of its product." />
    <label colspan="4" string="Important: please note that existing offered product lines will be removed." />
</form>"""

wrong_state_form = """<form string="Compute offered">
    <label colspan="4" string="This only applies to sale orders in 'Draft' state." />
</form>
"""

def do_compute_offered(wiz, cr, uid, data, context):
    so_id = data['ids'][0]
    o_so = pooler.get_pool(cr.dbname).get('sale.order')
    res = o_so._generate_offered(cr, uid, [so_id,], context)
    return dict()

def check_sale_order_state(wiz, cr, uid, data, context):
    so_id = data['ids'][0]
    o_so = pooler.get_pool(cr.dbname).get('sale.order')
    b_so = o_so.browse(cr, uid, so_id, context)
    return b_so.state == 'draft' and 'ask_confirmation' or 'not_draft'
    
class wizard_compute_offered(wizard.interface):
    __module__ = __name__
    states = {
        'init': 
            {
                'actions': [],
                'result': {
                    'type': 'choice',
                    'next_state' : check_sale_order_state,
                },
            },
        'ask_confirmation': 
            {
                'actions' : [],
                'result' : {
                    'type' : 'form',
                    'arch' : confirm_form, 
                    'fields' : dict(),
                    'state' : [
                        ('end','Cancel'),
                        ('do_it','Compute'),
                    ],
                },
            },
        'do_it' : 
            {
                'actions' : [do_compute_offered, ],
                'result' : {
                    'type' : 'state',
                    'state' : 'end',
                }
            },
        'not_draft' : 
            {
                'actions' : [],
                'result' : {
                    'type' : 'form',
                    'arch' : wrong_state_form,
                    'fields' : dict(),
                    'state' : [
                        ('end', 'Close'),
                    ],
                },
            },
    }

wizard_compute_offered('sale.order.compute.offered')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
