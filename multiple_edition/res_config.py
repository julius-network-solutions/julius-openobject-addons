# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today Julius Network Solutions SARL <contact@julius.fr>
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

# import copy
from openerp import models, fields, _

class ir_model(models.Model):
    _inherit = 'ir.model'

    multiple_edition_model = fields.Boolean('Multiple Edtion linked',
                                            help='If checked, by default the ' \
                                            'multiple edition configuration '\
                                            'will get this module in the list',
                                            default=False)

class multiple_edition_settings(models.TransientModel):
    _name = 'multiple.edition.settings'
    _inherit = 'res.config.settings'

    def _get_default_multiple_edition_models(self, cr, uid, context=None):
        return self.pool.get('ir.model').search(cr, uid, [('multiple_edition_model', '=', True)], context=context)

    models_ids = fields.Many2many('ir.model',
                                  'multiple_edition_settings_model_rel',
                                  'multiple_edition_id', 'model_id',
                                  'Models',
                                  domain=[('is_transient', '=', False)])

    _defaults = {
        'models_ids': _get_default_multiple_edition_models,
    }
    
    def update_field(self, cr, uid, vals, context=None):
        ## Init ##
        if context is None:
            context = {}
        model_ids = []
        model_obj = self.pool.get('ir.model')
        action_obj = self.pool.get('ir.actions.act_window')
        value_obj = self.pool.get('ir.values')
        ## Process ##
        if not vals or not vals.get('models_ids', False):
            return False
        elif vals.get('models_ids') or model_ids[0][2]:
            model_ids = vals.get('models_ids')
            if isinstance(model_ids[0], (list)):
                model_ids = model_ids[0][2]
        ### Unlink Previous Entries ###
        unlink_ids = action_obj.search(cr,  uid, [
                        ('res_model' , '=', 'multiple.edition')
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
                    ('multiple_edition_model', '=', True),
                ], context=context)
        model_obj.write(cr, uid, model_not_merge_ids, {'multiple_edition_model' : False}, context=context)
        
        # Put all models which are selected to be an object_merger
        model_obj.write(cr, uid, model_ids, {'multiple_edition_model' : True}, context=context)
          
        ### Create New Fields ###
        read_datas = model_obj.read(cr, uid, model_ids, ['model','name','multiple_edition_model'], context=context)
        for model in read_datas:
            act_id = action_obj.create(cr, uid, {
                 'name': "%s " % model['name'] + _("Multiple Edition"),
                 'type': 'ir.actions.act_window',
                 'res_model': 'multiple.edition',
                 'src_model': model['model'],
                 'view_type': 'form',
                 'context': "{'src_model':'%s','src_rec_id':active_id,"\
                 "'src_rec_ids':active_ids}" % (model['model']),
                 'view_mode':'form,tree',
                 'target': 'new',
            }, context=context)
            value_obj.create(cr, uid, {
                 'name': "%s " % model['name'] + _("Multiple Edition"),
                 'model': model['model'],
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(act_id),
            }, context=context)
        return True
    
    def create(self, cr, uid, vals, context=None):
        """ create method """
#         vals2 = copy.deepcopy(vals)
        vals2 = vals.copy()
        result = super(multiple_edition_settings, self).create(cr, uid, vals2, context=context)
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
