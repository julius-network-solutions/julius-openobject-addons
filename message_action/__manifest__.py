# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developped by 
# Copyright (c) 2020-Today Julius Network Solutions
# (http://www.julius.fr) All Rights Reserved.

{
    "name": "Automated Actions with mail messages",
    "version": "1.0",
    "category": "Tools",
    "author": "Julius Network Solutions",
    "contributors": [
                     "Mathieu Vatel <mathieu@julius.fr>",
                     ],
    "description": """
Automated Actions  with mail messages
=====================================


With this module you will be able to configure specific messages
to do some actions.

e.g.: Create an automatic stock move for a production lot.
""",
    "depends": [
                "mail",
                "stock",
                ],
    "data": [
            "security/ir.model.access.csv",
             "views/mail_message.xml",
             "views/mail_message_action.xml",
#              "data/accounting_assert_test_data.xml",
             ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
