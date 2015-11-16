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

class stock_move_scrap(orm.TransientModel):
    _inherit = 'stock.move.scrap'

    def _scrap_reason_get(self, cr, uid, context=None):
        reason_obj = self.pool.get('stock.move.scrap.reason')
        ids = reason_obj.search(cr, uid, [], context=context)
        result = []
        for line in reason_obj.browse(cr, uid, ids, context=context):
            result.append((line.id, line.name))

        result.append((-1, _('Other...')))
        return result

    _columns = {
        'reason': fields.selection(_scrap_reason_get,
                                 'Reason', size=-1,
                                 required=True,
                                 help="Reason for scraping."),
        'notes': fields.text('Notes'),
    }

    def move_scrap(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for data in self.browse(cr, uid, ids, context=context):
            context.update({
                'reason': data.reason,
                'notes_reason': data.notes,
            })
        return super(stock_move_scrap, self).move_scrap(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
