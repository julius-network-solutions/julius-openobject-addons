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

class res_partner(orm.Model):
    _inherit = "res.partner"
    
    _columns = {
        'admin_opposition': fields.many2one('admin.opposition', 'Admin opposition'),
    }

class admin_opposition(orm.Model):
    _name = "admin.opposition"
    _description = "Admin Opposition"
    
    _columns = {
        'code': fields.char('Code', size=64, required=True),
        'name': fields.char('Name', size=64, required=True),
        'block_order': fields.boolean('Block order'),
    }
    _defaults = {
        'block_order': True,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
