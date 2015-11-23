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
    "name": "Report print stored file",
    "category": "Base",
    "summary": "Print a file directly stored instead of report",
    "version": "0.1",
    "description": """
Report print stored file
========================

Version 0.1:
------------

    * Choose to print direcly a pdf file instead of using the report process
    * Allow to merge this pdf with the native report process (as layer)
""",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu VATEL <mathieu@julius.fr>",
    "depends": [
                "base",
                "report",
                ],
    "data": [
             "views/report.xml",
             ],
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
