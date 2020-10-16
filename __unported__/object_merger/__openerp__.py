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
    "name": "Object Merger",
    "version": "1.1",
    "category": "Tools",
    "description": """
Merge objects:
==============

This Module will give you the possibility to merge 2 or more objects together:
------------------------------------------------------------------------------

Example:
--------

    * You want to merge 2 partners, select the Partner to merge, then which one to keep.
    * All SO, PO, Invoices, Pickings, products, etc. of selected records will be add to the one to keep.

Version 1.1:
------------

    * Merge the linked attatchments, mails, etc.
    * Migrate to 8.0
""",
    "author": "Julius Network Solutions",
    "website": "http://www.julius.fr",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "depends": [
                "base",
                ],
    "data": [
             "wizard/object_merger_view.xml",
             "views/res_config_view.xml",
             ],
    "demo": [],
    "installable": True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
