.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================================
SALE STOCK BLOCK WITHOUT PAYMENT
================================

This module provides the ability to collect payment (advance) before
processing the delivery. Order should be paid before generating the label and
being shipped. It can be overridden for customers with a payment term.

It uses the due date of the invoice to determine if the order can be shipped:
* if the invoice is due (now > date_due) and state is not paid, block shipping.
* Otherwise, allow shipping.

Configuration
=============

* Go to Accounting > Configuration > Management > Payment Terms
* Select 'Immediate Payment'
* Enable 'Block Order Without Payment'

Usage
=====

* Create a customer and set his payment term to 'Immediate Payment'
* Create a quotation for this customer and confirm it
* Create the invoice and validate it
* Go back to the sales order to access the delivery order
* Try to process the delivery order. You can't because the invoice is due.

Known issues / Roadmap
======================

* ...

Credits
=======

Contributors
------------

* Julius Network Solutions SARL <contact@julius.fr>
* Mathieu Vatel <mathieu@julius.fr>
* Yvan Patry <yvan@julius.fr>
* Sandip Mangukiya <smangukiya@ursainfosystems.com>
* Maxime Chambreuil <mchambreuil@ursainfosystems.com>
