# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _

class account_tax(orm.Model):
    
    _inherit = 'account.tax'
   
    def regenerate_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        tax_code_ref = {}
        
        template = self.pool.get('account.chart.template').browse(cr, uid, 1, context=context)
        obj_tax_code_template = self.pool.get('account.tax.code.template')
        obj_acc_tax = self.pool.get('account.tax')
        obj_tax_temp = self.pool.get('account.tax.template')
        obj_acc_template = self.pool.get('account.account.template')
        obj_fiscal_position_template = self.pool.get('account.fiscal.position.template')

        # create all the tax code.
        tax_code_ref.update(obj_tax_code_template.generate_tax_code(cr, uid, template.tax_code_root_id.id, 1, context=context))

        # Generate taxes from templates.
        tax_templates = [x for x in template.tax_template_ids]
        generated_tax_res = obj_tax_temp._generate_tax(cr, uid, tax_templates, tax_code_ref, 1, context=context)
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
