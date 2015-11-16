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

import time

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
#            if line.move_id.state <> 'draft' and (not line.journal_id.entry_posted):
#                raise osv.except_osv(_('Error!'), _('You cannot do this modification on a confirmed entry. You can just change some non legal fields or you must unconfirm the journal entry first.\n%s.') % err_msg)
            if line.reconcile_id:
                raise osv.except_osv(_('Error!'), _('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: