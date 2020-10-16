# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models


class res_users(models.Model):
    _inherit = 'res.users'

    def copy(self, cr, uid, id, default=None, context=None):
        default = dict(default or {})
        if 'name' in default.keys() \
                and default.get('lastname') and default.get('firstname'):
            del default['name']
        return super(res_users, self).copy(cr, uid, id, default, context)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
