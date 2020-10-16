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
    "name": "Website authentication by SMS or Email",
    "summary": "Authentication by SMS or Email on the website",
    "category": "Website",
    "version": "1.5",
    "description": """
Website Authentication by SMS
=============================

Version 1.0:
------------

    * Generation of a code
    * Send the code to the partner (by sms)
    * Test and verify code used

Update 1.1:
-----------

    * Add the possibility to send the code by email instead of mobile
    * Format the phone number with the country code (depends of base_phone \
get it here: https://www.odoo.com/apps/modules/8.0/base_phone/)

Update 1.2:
-----------

    * Remove the dependency to base_phone, but create a new addons which \
is auto installed on base_phone installation \
"website_sms_authentication_base_phone"

Update 1.3:
-----------

    * Improve the website view with a different header if it's an email \
instead of a sms.

Update 1.4:
-----------

    * Improve the website view with an id on the first div "row mt16"
    * Get the values from the website view form

Update 1.5:
-----------

    * Improve the website view

""",
    "author": "Julius Network Solutions",
    "depends": [
                "smsclient",
                ],
    "data": [
             "views/sms_authentication.xml",
             "website_views/website_sms_authentication.xml",
             ],
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
