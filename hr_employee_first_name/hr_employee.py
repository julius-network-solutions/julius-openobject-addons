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

from openerp import fields, models, api, _

class resource_resource(models.Model):
    _inherit = 'resource.resource'
    
    last_name = fields.Char('Last Name', size=128, required=True)
    first_name = fields.Char('First Name', size=128)
    name = fields.Char('Name', store=True,
                       compute='_get_resource_name')
    
    def _auto_init(self, cr, context=None):
        res = super(resource_resource, self)._auto_init(cr, context=context)
        cr.execute('UPDATE resource_resource SET last_name = name '
                   'WHERE name IS NOT NULL AND last_name IS NULL;')
        return res

    @api.one
    @api.depends('last_name', 'first_name')
    def _get_resource_name(self):
        name = self.last_name and self.last_name.upper() or ''
        name += self.first_name and ' ' +  self.first_name.title() or ''
        self.name = name

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
