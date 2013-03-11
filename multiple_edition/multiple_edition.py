# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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

from lxml import etree
import openerp.tools
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class field_relation(orm.TransientModel):
    _name = 'field.relation'  
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(field_relation, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar,submenu)
        fields = {}
        xml = ''
        if context == None:
            context = {}
        multiple_edition_id = context.get('multiple_edition_id')
        if multiple_edition_id:
            field_data = self.pool.get('multiple.edition').browse(cr, uid, multiple_edition_id, context).field_id
            fields.update({'field_relation': {'type': field_data.ttype, 'relation': field_data.relation, 'string': field_data.name},})        
            xml_field = etree.Element('field', {'name':'field_relation'})
            root = xml_field.getroottree()
            xml = etree.tostring(root)
            fields.update(result['fields'])
            result['fields'] = fields
        result['arch'] = result['arch'].replace('<separator string="placeholder"/>',xml)
        return result
    
    def create(self, cr, uid, vals, context=None):
        data = vals.get('field_relation')
        return super(field_relation, self).create(cr, uid, vals, context=context)
          
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        result = super(field_relation, self).read(cr, uid, ids, fields, context, load)
        if context == None:
            context = {}
        context.update('')
        
        return result
    
    def save_relations(self, cr, uid, ids, context=None):
#        multiple_edition_data = self.pool.get('multiple.edition').browse(cr, uid, , context)
#        for this in self.browse(cr, uid, ids, context=context):
#            test = this.field_relation
        if context == None:
            context = {}
        context.update({'value_ok':True})
        return {
            'name': _('Result'),
            'res_id': context.get('multiple_edition_id'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'multiple.edition',
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
        }

class multiple_edition(orm.TransientModel):
    
    _name = 'multiple.edition'    
    
    def _get_default_multiple_edition_model(self, cr, uid, context=None):
        model_obj = self.pool.get('ir.model')
        if context is None:
            context = {}
        print context
        temp = context.get('active_model')
        model_ids = model_obj.search(cr, uid, [('model', '=', temp)], limit=1, context=context)
        if model_ids:
            result = model_ids[0]
        return result
    
    _columns = {
        'model_id': fields.many2one('ir.model', 'Resource', readonly=True, required=True),
        'field_type': fields.selection([('char', 'Char'),
                                        ('boolean', 'Boolean'),
                                        ('integer', 'Integer'),
                                        ('text', 'Text'),
                                        ('many2one', 'Many2One'),
                                        ('one2many', 'One2Many'),
                                        ('many2many', 'Many2Many'),
                                        ('float','Float'),
                                        ], 'Type of Field', required=True),
        'field_id': fields.many2one('ir.model.fields', 'Field', required=True, domain="[('model_id', '=', model_id),('ttype', '=', field_type)]"),
        'char_value': fields.char('Value', size=256),
        'bool_value': fields.boolean('Value'),
        'int_value': fields.integer('Value'),
        'text_value': fields.text('Value'),
        'float_value': fields.float('Value'),
        
    }
    
    _defaults = {
        'model_id': _get_default_multiple_edition_model,
    }
    
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(multiple_edition, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar,submenu)
        xml = ''
        if context is None:
            context = {}
        if context.get('value_ok'):
            fields = {}
            multiple_edition_id = context.get('multiple_edition_id')
            field_data = self.pool.get('multiple.edition').browse(cr, uid, multiple_edition_id, context).field_id
            fields.update({'field_relation': {'type': field_data.ttype, 'relation': field_data.relation, 'string': field_data.name},})        
            xml_field = etree.Element('field', {'name':'field_relation'})
            root = xml_field.getroottree()
            xml = etree.tostring(root)
            fields.update(result['fields'])
            result['fields'] = fields
        result['arch'] = result['arch'].replace('<separator string="placeholder"/>',xml)
        return result
        
    def edit_fields(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        update_ids = context and context.get('active_ids') or []
        for this in self.browse(cr, uid, ids, context=context):
            if this.field_type == 'char':
                value = this.char_value
            elif this.field_type == 'boolean':
                value = this.bool_value
            elif this.field_type == 'integer':
                value = this.int_value
            elif this.field_type == 'text':
                value = this.text_value
            elif this.field_type == 'float':
                value = this.float_value
            if value:
                model_obj = self.pool.get(this.model_id.model)
                for update_id in update_ids:
                    model_obj.write(cr, uid, update_id, {this.field_id.name: value}, context)
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
