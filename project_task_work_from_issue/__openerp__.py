# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-Today Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Task work from issue",
    "summary" : "Create task work from an issue",
    "version": "1.0",
    "author": "Julius Network Solutions",
    "website": "http://www.julius.fr",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    'category': 'Project Management',
    "depends": [
                "project",
                "project_issue",
                ],
    "description": """
Allow the user to create a task work directly from an issue
""",
    "demo": [],
    "data": [
             "views/project_issue.xml", 
             ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
