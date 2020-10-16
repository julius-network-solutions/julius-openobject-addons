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

from openerp import models, api, _
import re


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def name_get(self):
        res = super(res_partner, self).name_get()
        res_dict = dict(res)
        res2 = []
        for record in self:
            address_type = ""
            ref = record.ref
            if record.type == 'invoice':
                address_type = _("Inv")
            elif record.type == 'delivery':
                address_type = _("Deli")
            if not ref and record.parent_id:
                ref = record.parent_id.ref
            prefix = ""
            if ref and address_type:
                prefix = '[%s - %s]' % (ref, address_type)
            elif ref:
                prefix = '[%s]' % ref
            elif address_type:
                prefix = '[%s]' % address_type
            partner_name = res_dict.get(record.id, '')
            new_name = "%s %s" % (prefix, partner_name)
            res2.append((record.id, new_name))
        return res2

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name:
            records = self.search([('ref', '=', name)] + args, limit=limit)
            if records:
                    new_limit = (limit and (limit-len(records)) or False)
                    records |= self.\
                        search([('parent_id', 'child_of', records.ids)],
                               limit=new_limit)
            else:
                records = self.search(args + [('ref', operator, name)],
                                      limit=limit)
                if not limit or len(records) < limit:
                    records += self.\
                        search(args + [('name', operator, name)],
                               limit=(limit and (limit-len(records)) or False))
                    if records:
                        new_limit = (limit and (limit-len(records)) or False)
                        records |= self.\
                            search([('parent_id', 'child_of', records.ids)],
                                   limit=new_limit)
            if not records:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    records = self.search([('ref', '=', res.group(2))] + args,
                                          limit=limit)
                if records:
                    new_limit = (limit and (limit-len(records)) or False)
                    records |= self.\
                        search([('parent_id', 'child_of', records.ids)],
                               limit=new_limit)
            if records:
                return records.name_get()
        return super(res_partner, self).\
            name_search(name, args=args, operator=operator, limit=limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
