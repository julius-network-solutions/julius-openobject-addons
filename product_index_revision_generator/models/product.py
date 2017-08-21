# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, fields, api, _
from odoo.osv import expression
from openerp.exceptions import ValidationError
from openerp.tools.safe_eval import safe_eval
import string
import re


def find_next_revision_index(letters=None):
    try:
        alpha = string.ascii_uppercase
        if len(letters) == 0 or letters is None:
            return 'A'
        last_letter = letters[-1]
        if last_letter in alpha:
            keep_letters = letters[0:-1]
            last_letter_num = alpha.find(last_letter)
        else:
            return letters + 'A'
        if last_letter_num == 25:
            if keep_letters == '':
                keep_letters = find_next_revision_index('')
                next_letter = 'A'
            else:
                keep_letters = find_next_revision_index(keep_letters)
                next_letter = 'A'
        else:
            next_letter_num = last_letter_num + 1
            next_letter = alpha[next_letter_num]
        return keep_letters + next_letter
    except:
        return 'A'


class product_product(models.Model):
    _inherit = 'product.product'

    _order = 'default_code,revision_index DESC,id'

    date_start = fields.Date('Valid From')
    date_stop = fields.Date('Valid Until')
    revision_index = fields.Char(default='')
    revision_note = fields.Text(default='')
    plan_revision = fields.Char()
    plan_document = fields.Binary('Plan', related='plan_document_id.datas',
                                  store=False, readonly=True)
    plan_document_id = fields.Many2one('ir.attachment', 'Plan',
                                       compute='_get_plan_document_id',
                                       store=False)

    @api.one
    def _get_plan_document_id(self):
        attachment_obj = self.env['ir.attachment']
        attachments = attachment_obj.\
            search([
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'product.product'),
                    ('is_plan', '=', True)
                    ], limit=1)
        self.plan_document_id = attachments.id

    @api.one
    @api.constrains('default_code', 'revision_index')
    def _check_revision_index(self):
        """
        Check if there's already an article with same revision
        and default code
        """
        if self.default_code:
            domain = [
                      ('default_code', '=', self.default_code),
                      ('id', '!=', self.id),
                      ]
            if self.revision_index:
                domain += [
                           '|',
                           ('revision_index', '=', False),
                           ('revision_index', '=', self.revision_index),
                           ]
            if self.search(domain):
                raise ValidationError(_("The article '%s' with revision '%s' "
                                        "already exists")
                                      % (self.default_code,
                                         self.revision_index))
        return True

    def create_revision_index(self):
        generator_obj = self.env['product.revision.generator']
        generator_line_obj = self.env['product.revision.generator.line']
        bom_obj = self.env['mrp.bom']
        action = False
        try:
            action = self.env.ref('product_index_revision_generator.'
                                  'action_product_revision_generator')
        except ValueError:
            raise ValidationError(_('Error'),
                                  _('Action "Product index generator" '
                                    'not found in the system'))
        if action:
            action = action.read()[0]
            action_context = action.get('context', {})
            action_context = safe_eval(action_context)
            action_context.update({'default_product_id': self.id,})
            action['context'] = action_context
            vals = {'name': 'A', 'product_id': self.id,}
            if self.revision_index:
                index = self.revision_index
                vals.update({
                             'name': find_next_revision_index(index),
                             })
            boms = bom_obj.search([
                                   ('product_id', '=', self.id),
                                   ], limit=1)
            if not boms:
                boms = bom_obj.search([
                                       ('product_tmpl_id', '=', self.product_tmpl_id.id),
                                       ], limit=1)
            if boms:
                vals.update({
                             'origin_bom_id': boms.id,
                             })
            gen = generator_obj.with_context(action_context).create(vals)
            if boms:
                for line in boms.bom_line_ids:
                    list_line_vals = line.copy_data()
                    line_vals = list_line_vals and list_line_vals[0] or {}
                    line_vals.pop('bom_id', None)
                    line_vals.update({'generator_id': gen.id})
                    generator_line_obj.create(line_vals)
            action['res_id'] = gen.id
        return action

    # TODO: See if this needs to be migrated or not
#     def _get_partner_code_name(self, cr, uid, ids, product,
#                                partner_id, context=None):
#         res = super(product_product, self).\
#             _get_partner_code_name(cr, uid, ids, product,
#                                    partner_id, context=context)
#         if res.get('code') and res['code'] == product.default_code:
#             if product.revision_index:
#                 res['code'] += ' (%s)' % product.revision_index
#         return res

    @api.multi
    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            revision_index = self._context.get('display_revision_index', True) and d.get('revision_index', False) or False
            if code:
                if revision_index:
                    code = '%s (%s)' % (code, revision_index)
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        for product in self.sudo():
            # display only the attributes with multiple possible values on the template
            variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
            variant = product.attribute_value_ids._variant_name(variable_attributes)

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
                if not sellers:
                    sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          'revision_index': product.revision_index,
                          }
                result.append(_name_get(mydict))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            products = self.env['product.product']
            if operator in positive_operators:
                products = self.search([('default_code', '=', name)] + args, limit=limit)
                if not products:
                    products = self.search([('barcode', '=', name)] + args, limit=limit)
            if not products and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                products = self.search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(products) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(products)) if limit else False
                    products += self.search(args + [('name', operator, name), ('id', 'not in', products.ids)], limit=limit2)
            elif not products and operator in expression.NEGATIVE_TERM_OPERATORS:
                products = self.search(args + ['&', ('default_code', operator, name), ('name', operator, name)], limit=limit)
            if not products and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    default_code = res.group(2)
                    index = False
                    ptrn2 = re.compile('(.*? \(.*?\))')
                    res2 = ptrn2.search(default_code)
                    if res2:
                        code = res2.group(1).split(' (')
                        if code:
                            default_code = code[0]
                        if len(code) > 1:
                            index = code[1].split(')')[0]
                    search_domain = [('default_code','=', default_code)]
                    if index:
                        search_domain += [('revision_index', '=', index)]
                    products = self.search(search_domain + args, limit=limit)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not products and self._context.get('partner_id'):
                suppliers = self.env['product.supplierinfo'].search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                if suppliers:
                    products = self.search([('product_tmpl_id.seller_ids', 'in', suppliers.ids)], limit=limit)
        else:
            products = self.search(args, limit=limit)
        return products.name_get()


class product_template(models.Model):
    _inherit = 'product.template'

    date_start = fields.Date('Valid From', related="product_variant_id.date_start")
    date_stop = fields.Date('Valid Until', related="product_variant_id.date_stop")
    revision_index = fields.Char(default='', related="product_variant_id.revision_index")
    revision_note = fields.Text(default='', related="product_variant_id.revision_note")
    plan_revision = fields.Char(related="product_variant_id.plan_revision")
    plan_document = fields.Binary('Plan', related='product_variant_id.plan_document',
                                  store=False, readonly=True)
    plan_document_id = fields.Many2one('ir.attachment', 'Plan',
                                       related="product_variant_id.plan_document_id")

    @api.one
    def _get_plan_document_id(self):
        attachment_obj = self.env['ir.attachment']
        attachments = attachment_obj.\
            search([
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'product.product'),
                    ('is_plan', '=', True)
                    ], limit=1)
        self.plan_document_id = attachments.id

    def create_revision_index(self):
        return self.product_variant_id.create_revision_index()

    @api.multi
    def name_get(self):
        return [
                (template.id, '%s%s' % (template.default_code and \
                                        '[%s%s] ' % (template.default_code,
                                                     template.revision_index and \
                                                     ' (%s)' % template.revision_index or '') or '',
                                          template.name))
                for template in self]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
