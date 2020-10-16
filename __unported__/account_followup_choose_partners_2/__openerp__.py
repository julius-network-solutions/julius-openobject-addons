# -*- coding: utf-8 -*-


{
    'name': 'Payment Follow-up Management Choose partners 2',
    'version': '2.0',
    'category': 'Accounting & Finance',
    'description': """
This module will adds a step to send the letters to the customers.
Choose a partner by boolean in list of partner (customer, followup)
and in menu 'others options' click on 'Make followup' and follow workflow

You can personnalize letters in native menu of account_followup V8
'menu accounting -> Configuration -> Followup -> Leve of followup'

""",
    'author': 'Julius Network Solutions',
    'website': 'http://www.julius.fr',
    'images': [],
    'depends': ['account_followup'],
    'data': [
        'wizard/account_followup_print_view.xml',
    ],
    'demo': ['account_followup_demo.xml'],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
