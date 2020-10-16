# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developped by 
# Copyright (c) 2020-Today Julius Network Solutions
# (http://www.julius.fr) All Rights Reserved.

{
    "name": "Automated Actions with mail messages",
    "version": "1.0.5",
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

Version History:
================


Version 1.0.5:
--------------

    * Keep the package info of the ProdLot.
    * Add an option to keep or not in the package.
    * Fill the origin of the picking with the value set in the "action".
    * Define which user is automatically executing the "action".
    * Create a cron executing the action once a day.


Version 1.0.4:
--------------

Create a move and a picking and validate them "manually" with the button
in the message.
""",
    "depends": [
                "mail",
                "stock",
                ],
    "data": [
             "security/ir.model.access.csv",
             "data/cron.xml",
             "views/mail_message.xml",
             "views/mail_message_action.xml",
             ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
