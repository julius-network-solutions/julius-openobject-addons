# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, fields, _

class product_category(models.Model):
    _inherit = 'product.category'

    sale_taxes_ids = fields.Many2many('account.tax',
                                      'product_cat_tax_cust_rel',
                                      'cat_id', 'tax_id', string='Sales Taxes',
                                      domain=[('parent_id', '=', False),
                                              ('type_tax_use', 'in', ['sale',
                                                                      'all'])])
    purchase_taxes_ids = fields.Many2many('account.tax',
                                          'product_cat_tax_supp_rel',
                                          'cat_id', 'tax_id',
                                          string='Purchase Taxes',
                                          domain=[('parent_id', '=', False),
                                                  ('type_tax_use', 'in',
                                                   ['purchase','all'])])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
