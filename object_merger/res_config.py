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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import copy

class ir_model(orm.Model):
    _inherit = 'ir.model'
    
    _columns = {
        'object_merger_model': fields.boolean('Object Merger',
            help='If checked, by default the Object Merger configuration will get this module in the list'),
    }
    
    _defaults = {
        'object_merger_model': False,
    }

class object_merger_settings(orm.TransientModel):
    _name = 'object.merger.settings'
    _inherit = 'res.config.settings'
    
    def _get_default_object_merger_models(self, cr, uid, context=None):
        return self.pool.get('ir.model').search(cr, uid, [('object_merger_model', '=', True)], context=context)
    
    _columns = {
        'models_ids': fields.many2many('ir.model',
            'object_merger_settings_model_rel',
            'object_merger_id', 'model_id', 'Models', domain=[('osv_memory', '=', False)]),
    }
    
    _defaults = {
        'models_ids': _get_default_object_merger_models,
    }
    
    def update_field(self, cr, uid, vals, context=None):
        ## Init ##
        if context is None:
            context = {}
        model_ids = []
        model_obj = self.pool.get('ir.model')
        action_obj = self.pool.get('ir.actions.act_window')
        value_obj = self.pool.get('ir.values')
        field_obj = self.pool.get('ir.model.fields')
        ## Process ##
        if not vals or not vals.get('models_ids', False):
            return False
        elif vals.get('models_ids') or model_ids[0][2]:
            model_ids = vals.get('models_ids')
            if isinstance(model_ids[0], (list)):
                model_ids = model_ids[0][2]
        # Unlink Previous Actions
        unlink_ids = action_obj.search(cr,  uid, [
                        ('res_model' , '=', 'object.merger')
                    ], context=context)
        for unlink_id in unlink_ids:
            action_obj.unlink(cr, uid, unlink_id)
            un_val_ids = value_obj.search(cr, uid,[
                ('value' , '=',"ir.actions.act_window," + str(unlink_id)),
                ], context=context)
            value_obj.unlink(cr, uid, un_val_ids, context=context)
        # Put all models which were selected before back to not an object_merger
        model_not_merge_ids = model_obj.search(cr, uid, [
                    ('id', 'not in', model_ids),
                    ('object_merger_model', '=', True),
                ], context=context)
        model_obj.write(cr, uid, model_not_merge_ids, {'object_merger_model' : False}, context=context)
        
        # Put all models which are selected to be an object_merger
        model_obj.write(cr, uid, model_ids, {'object_merger_model' : True}, context=context)
          
        ### Create New Fields ###
        object_merger_ids = model_obj.search(cr, uid, [
                    ('model', '=', 'object.merger')
                ], context=context)
        read_datas = model_obj.read(cr, uid, model_ids, ['model','name','object_merger_model'], context=context)
        for model in read_datas:
            field_name = 'x_' + model['model'].replace('.','_') + '_id'
            act_id = action_obj.create(cr, uid, {
                 'name': "%s " % model['name'] + _("Merger"),
                 'type': 'ir.actions.act_window',
                 'res_model': 'object.merger',
                 'src_model': model['model'],
                 'view_type': 'form',
                 'context': "{'field_to_read':'%s'}" % field_name,
                 'view_mode':'form',
                 'target': 'new',
            }, context=context)
            value_obj.create(cr, uid, {
                 'name': "%s " % model['name'] + _("Merger"),
                 'model': model['model'],
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(act_id),
            }, context=context)
            field_name = 'x_' + model['model'].replace('.','_') + '_id'
            if not field_obj.search(cr, uid, [
                ('name', '=', field_name),
                ('model', '=', 'object.merger')], context=context):
                field_data = {
                    'model': 'object.merger',
                    'model_id': object_merger_ids and object_merger_ids[0] or False,
                    'name': field_name,
                    'relation': model['model'],
                    'field_description': "%s " % model['name'] + _('To keep'),
                    'state': 'manual',
                    'ttype': 'many2one',
                }
                field_obj.create(cr, SUPERUSER_ID, field_data, context=context)
        return True
    
    def create(self, cr, uid, vals, context=None):
        """ create method """
        vals2 = copy.deepcopy(vals)
        result = super(object_merger_settings, self).create(cr, uid, vals2, context=context)
        ## Fields Process ##
        self.update_field(cr, uid, vals, context=context)
        return result
    
    def install(self, cr, uid, ids, context=None):
#       Initialization of the configuration
        if context is None:
            context = {}
        """ install method """
        for vals in self.read(cr, uid, ids, context=context):
            result = self.update_field(cr, uid, vals, context=context)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
