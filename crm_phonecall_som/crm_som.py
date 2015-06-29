# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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

import time
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _

#
# Partner: State of Mind
#
class res_partner_som(osv.osv):
    _name = "res.partner.som"
    _columns = {
        'name': fields.char('State of Mind',size=64, required=True),
        'factor': fields.float('Factor', required=True)
    }
res_partner_som()

class crm_phonecall(osv.osv):
    _inherit = "crm.phonecall"

    _columns = {
        'som': fields.many2one('res.partner.som', 'State of Mind'),
    }

crm_phonecall()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

