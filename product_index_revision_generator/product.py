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

from openerp.osv import fields, orm
from openerp.tools.translate import _
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

class product_product(orm.Model):
    _inherit = 'product.product'

    _order = 'default_code,revision_index DESC,name_template'
    def _get_plan_document_id(self, cr, uid,
                              ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        attachment_obj = self.pool.get('ir.attachment')
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = False
            att_ids = attachment_obj.search(cr, uid, [
                ('res_id', '=', product.id),
                ('res_model', '=', 'product.product'),
                ('is_plan', '=', True)
                ], context=context, limit=1)
            if att_ids:
                res[product.id] = att_ids[0]
        return res

    def _get_partner_code_name(self, cr, uid, ids, product,
                               partner_id, context=None):
        res = super(product_product, self).\
            _get_partner_code_name(cr, uid, ids, product,
                                   partner_id, context=context)
        if res.get('code') and res['code'] == product.default_code:
            if product.revision_index:
                res['code'] += ' (%s)' %product.revision_index
        return res

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name','')
            code = d.get('default_code',False)
            index = d.get('revision_index', False)
            if code:
                if index:
                    name = '[%s (%s)] %s' % (code,index,name)
                else:
                    name = '[%s] %s' % (code,name)
            if d.get('variants'):
                name = name + ' - %s' % (d['variants'],)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)

        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                              'id': product.id,
                              'name': s.product_name or product.name,
                              'default_code': s.product_code or product.default_code,
                              'variants': product.variants
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': product.name,
                          'default_code': product.default_code,
                          'revision_index': product.revision_index,
                          'variants': product.variants
                          }
                result.append(_name_get(mydict))
        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            if not ids:
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
                    ids = self.search(cr, user, search_domain + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    _columns = {
        'date_start': fields.date('Valid From',),
        'date_stop': fields.date('Valid Until',),
        'revision_index': fields.char('Revision Index', size=128),
        'revision_note': fields.text('Revision note'),
        'plan_revision': fields.char('Plan Revision', size=128),
        'plan_document_id': fields.function(_get_plan_document_id,
                                            type="many2one",
                                            string="Plan",
                                            relation="ir.attachment",
                                            store=False),
        'plan_document': fields.related('plan_document_id', 'datas',
                                        type="binary",
                                        string="Plan",
                                        store=False,
                                        readonly=True,
                                        ),
    }

    _defaults = {
        'revision_index': '',
        'revision_note': '',
    }

    def create_revision_index(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_obj = self.pool.get('ir.model.data')
        action_obj = self.pool.get('ir.actions.act_window')
        generator_obj = self.pool.get('product.revision.generator')
        generator_line_obj = self.pool.get('product.revision.generator.line')
        bom_obj = self.pool.get('mrp.bom')
        action = False
        for product in self.browse(cr, uid, ids, context=context):
            try:
                model, action_id = data_obj.\
                    get_object_reference(cr, uid,
                                         'product_index_revision_generator',
                                         'action_product_revision_generator')
            except:
                raise orm.except_orm('Error',
                                     'Action "Product index generator" ' \
                                     'not found in the system')
            if action_id:
                action = action_obj.read(cr, uid, action_id, context=context)
                action_context = action.get('context', {})
                action_context = safe_eval(action_context)
                action_context.update({'default_product_id': product.id,})
                action['context'] = action_context
                vals = {'name': 'A'}
                if product.revision_index:
                    index = product.revision_index
                    vals.update({
                        'name': find_next_revision_index(index),
                        })
                bom_ids = bom_obj.search(cr, uid, [
                    ('product_id', '=', product.id),
                    ('bom_id', '=', False),
                    ], limit=1, context=context)
                bom_id = False
                if bom_ids:
                    bom_id = bom_ids[0]
                    vals.update({'origin_bom_id': bom_id})
                gen_id = generator_obj.create(cr, uid, vals, action_context)
                if bom_id:
                    for line in bom_obj.\
                        browse(cr, uid, bom_id, context=context).bom_lines:
                        line_vals = bom_obj.\
                            copy_data(cr, uid, line.id, context=context)
                        line_vals.update({'generator_id': gen_id})
                        generator_line_obj.\
                            create(cr, uid, line_vals, context=context)
                action['res_id'] = gen_id
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
