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
    "name": "Document Signed",
    "summary": "Sign your attachment with an ssl key",
    "version": "0.2",
    "category": "Knowledge Management",
    "description": """
Sign your attachments
=====================

Setting:
--------

    * Please install these python libs:
        * M2Crypto (https://pypi.python.org/pypi/M2Crypto)
        * base64 (https://pymotw.com/2/base64/)
        * hashlib (https://pypi.python.org/pypi/hashlib)
    * Please install:
        * openssl (https://www.openssl.org/)

Generate your key like this (on linux):
---------------------------------------

openssl req -x509 -newkey rsa:2048 -keyout mykey.pem -out cert.pem -days 365

Then:
-----

    * Go to "Settings > Configuration > General Settings"
    * Set the name of your generated key
    * Set your pass phrase used for this key

In the attachment you will find a button to sign the document.

How to check this ?
-------------------

    * The signature will be added to this attachment as an other attachment.
    * You will find a wizard to test a document.
""",
    "author": "Julius Network Solutions",
    "contributors": "Mathieu Vatel <mathieu@julius.fr>",
    "website": "http://www.julius.fr/",
    "images": [],
    "depends": [
                "base",
                "base_setup",
                "document",
                ],
    "data": [
             "wizard/test_attachment.xml",
             "views/attachment_view.xml",
             "views/res_config_view.xml",
             ],
    "demo": [],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
