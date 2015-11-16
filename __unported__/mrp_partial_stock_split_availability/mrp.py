# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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

class mrp_production(orm.Model):
    _inherit = "mrp.production"

    def _create_move_to_do(self, cr, uid, move_id,
                           quantity_to_do, context=None):
        if context is None: context = {}
        new_id = False
        return new_id

    def _write_move_to_do(self, cr, uid, move_id,
                          quantity_ready, context=None):
        if context is None: context = {}
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
