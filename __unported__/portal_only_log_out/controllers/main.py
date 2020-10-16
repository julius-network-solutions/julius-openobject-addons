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

from openerp.addons.web.controllers.main import Session
from openerp.http import request

class InheritSession(Session):

    def session_info(self):
        res = super(InheritSession, self).session_info()
        cr = request.env.cr
        portal = True
        if request.env.user:
            cr.execute("""SELECT 1 FROM res_groups_users_rel
                       WHERE uid=%s AND gid IN
                       (SELECT res_id FROM ir_model_data WHERE
                       module=%s AND name=%s)""",
                       (request.env.user.id, 'base', 'group_portal'))
            portal = bool(cr.fetchone())
        group_portal = portal if request.session.uid else None
        res.update({'portal_user': group_portal and 1 or 0})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
