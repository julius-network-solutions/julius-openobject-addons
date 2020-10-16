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

{
    'name': 'Attendance for partner',
    'summary': 'Manage attendances for partner',
    'version': '1.0',
    'category': 'Human resources',
    'description': """
Presentation:
=============

This module will adds the field "Partner" to the attendance to be able to track partner's attendance.

This can be use for child care for example.
""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'contibutors': 'Mathieu Vatel <mathieu@julius.fr>',
    'depends': [
                'hr_attendance',
                ],
    'data': [
             'wizard/password_validation_view.xml',
             'wizard/point_attendance_view.xml',
             'hr_attendance.xml',
             'partner_attendance.xml',
             'partner.xml',
             ],
    'demo': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
