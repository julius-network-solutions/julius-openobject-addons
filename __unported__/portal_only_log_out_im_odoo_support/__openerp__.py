# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

{
    "name": "Portal user with only 'Log out' with support",
    "summary": "Hide all menus in User Menu except 'Log Out' for portal users",
    "version": '1.0',
    "description": """
Update the UserMenu:
====================

This is keeping only "Log Out" for all users of portal group.
""",
    "author": 'Julius Network Solutions',
    "contributors": 'Mathieu Vatel <mathieu@julius.fr>',
    "website": 'http://www.julius.fr/',
    "depends": [
        'portal_only_log_out',
        'im_odoo_support',
    ],
    "data": [],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    "demo": [],
    "auto_install": True,
    "category" : "Portal",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
