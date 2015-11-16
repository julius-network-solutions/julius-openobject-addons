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

from openerp.osv import orm, fields
from openerp.tools.translate import _

class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_follow_up_level(self, cr, uid, ids,
                             name, args, context=None):
        if context is None:
            context = {}
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            val = False
            if partner.parent_id:
                parent = partner.parent_id
                val = parent.latest_followup_level_id and \
                    parent.latest_followup_level_id.name or False
            if not val:
                val = partner.latest_followup_level_id and \
                    partner.latest_followup_level_id.name or False
            res[partner.id] = val
        return res
        

    _columns = {
        'followup_level': fields.function(_get_follow_up_level,
            type='char', size=128, string='Follow up level', store=False),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: