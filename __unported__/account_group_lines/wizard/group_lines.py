# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, _

class account_group_move_line(models.TransientModel):
    _name = 'account.group.move.line'
    
    def group_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('account.move')
        merger = self.browse(cr, uid, ids[0], context=context)
        if context.get('active_ids', False):
            move_obj.action_group_lines(cr, uid, context.get('active_ids', False), context)
        self.unlink(cr, uid, ids, context=context)
        return {'ir.actions.act_window':'close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: