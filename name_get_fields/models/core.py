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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, api


class name_get_inherited(models.AbstractModel):
    _name = 'name.get.inherited'
    _description = 'Name get inherited'

    @api.multi
    def name_get(self):
        fields = self._context.get('name_get_fields')
        if fields:
            reads = self.read(fields)
            result = []
            for record in reads:
                names = []
                for field in fields:
                    if record.get(field) and record[field]:
                        if isinstance(record[field], tuple) and \
                                len(record[field]) >= 2:
                            names.append(record[field][1])
                        else:
                            names.append(record[field])
                name = ' / '.join(names)
                result.append((record['id'], "%s" % (name)))
                return result
        return super(name_get_inherited, self).name_get()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
