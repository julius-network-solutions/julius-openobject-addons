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
    
    def _generate_tax(self, cr, uid, tax_templates, tax_code_template_ref, company_id, context=None):
        """
        This method generate taxes from templates.

        :param tax_templates: list of browse record of the tax templates to process
        :param tax_code_template_ref: Taxcode templates reference.
        :param company_id: id of the company the wizard is running for
        :returns:
            {
            'tax_template_to_tax': mapping between tax template and the newly generated taxes corresponding,
            'account_dict': dictionary containing a to-do list with all the accounts to assign on new taxes
            }
        """
        if context is None:
            context = {}
        res = {}
        todo_dict = {}
        tax_template_to_tax = {}
        for tax in tax_templates:
            vals_tax = {
                'name':tax.name,
                'sequence': tax.sequence,
                'amount': tax.amount,
                'type': tax.type,
                'applicable_type': tax.applicable_type,
                'domain': tax.domain,
                'parent_id': tax.parent_id and ((tax.parent_id.id in tax_template_to_tax) and tax_template_to_tax[tax.parent_id.id]) or False,
                'child_depend': tax.child_depend,
                'python_compute': tax.python_compute,
                'python_compute_inv': tax.python_compute_inv,
                'python_applicable': tax.python_applicable,
                'base_code_id': tax.base_code_id and ((tax.base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.base_code_id.id]) or False,
                'tax_code_id': tax.tax_code_id and ((tax.tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.tax_code_id.id]) or False,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_code_id': tax.ref_base_code_id and ((tax.ref_base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_base_code_id.id]) or False,
                'ref_tax_code_id': tax.ref_tax_code_id and ((tax.ref_tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_tax_code_id.id]) or False,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'include_base_amount': tax.include_base_amount,
                'description': tax.description,
                'company_id': company_id,
                'type_tax_use': tax.type_tax_use,
                'price_include': tax.price_include
            }
            new_tax_ids = self.pool.get('account.tax').search(cr, uid, [('description', '=', tax.description),('company_id', '=', company_id)], context=context)
            if new_tax_ids:
                self.pool.get('account.tax').write(cr, uid, new_tax_ids[0], vals_tax)
                new_tax = new_tax_ids[0]
            else:
                new_tax = self.pool.get('account.tax').create(cr, uid, vals_tax)
            tax_template_to_tax[tax.id] = new_tax
            #as the accounts have not been created yet, we have to wait before filling these fields
            todo_dict[new_tax] = {
                'account_collected_id': tax.account_collected_id and tax.account_collected_id.id or False,
                'account_paid_id': tax.account_paid_id and tax.account_paid_id.id or False,
            }
        res.update({'tax_template_to_tax': tax_template_to_tax, 'account_dict': todo_dict})
        return res

   
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
