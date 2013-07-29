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

class clean_pricelist_data(orm.Model):
    _name = 'clean.pricelist.data'
    
    _columns = {}
    
    def clean_pricelist_data(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        offset = 370
        while offset < 1000:
            partner_ids = partner_obj.search(cr, uid, [
                ('is_company', '=', True),
    #            ('list_to_compute', '=', True),
            ], limit=10, offset=offset, context=context)
            partner_obj._create_update_pricelist(cr, uid, partner_ids, context=context)
            offset += 10
            cr.commit()
        version_obj = self.pool.get('product.pricelist.version')
        version_ids = version_obj.search(cr, uid,
            [('active', '=', False)], context=context)
        if version_ids:
            version_obj.unlink(cr, uid, version_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
