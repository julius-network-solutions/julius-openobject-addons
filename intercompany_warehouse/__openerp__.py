# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Inter Company Warehouse",
    "version": "1.0",
    "depends": [
        "stock",
        "intercompany_sale_purchase",
        "stock_picking_location",
        "stock_production_lot_current_location",
    ],
    "author": "Julius Network Solutions",
    'images': [],
    "description": """
Inter Company Warehouse module
====================================
This Inter company warehouse module provides:
--------------------------------------------
    * Automatic creation of an incoming shipment linked to the delivery order when you use the native sale / purchase to an partner linked to a system company.
    * Automatic fill-in serial numbers to the move lines on the reception if the delivery have serial defined.

You will have to install "intercompany_sale_purchase", "stock_picking_location" and "stock_production_lot_current_location" modules.
    """,
    "website": "http://julius.fr",
    "category": "Tools",
    "demo": [],
    "data": [
        "stock_view.xml",
        "data/location_data.xml",
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
