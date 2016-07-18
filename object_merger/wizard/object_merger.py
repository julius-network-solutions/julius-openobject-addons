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

from openerp.osv import fields as old_fields
from openerp.tools import ustr
from openerp import api, models, fields, _
from openerp.exceptions import except_orm

import logging
_logger = logging.getLogger(__name__)

class object_merger(models.TransientModel):
    """
    Merges objects
    """
    _name = 'object.merger'
    _description = 'Merge objects'

    name = fields.Char()
    delete_if_not_active = fields.Boolean('Delete records if not active field',
                                          default=False)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(object_merger, self).\
            fields_view_get(cr, uid, view_id, view_type,
                            context=context, toolbar=toolbar, submenu=False)
        object_ids = context.get('active_ids',[])
        active_model = context.get('active_model')
        field_name = 'x_' + (active_model and active_model.replace('.','_') or '') + '_id'
        res_fields = res['fields']
        if object_ids:
            view_part = """<label for='""" + field_name + """'/>
                    <div>
                        <field name='""" + field_name + \
                        """' required="1" domain="[(\'id\', \'in\', """ + \
                        str(object_ids) + """)]"/>
                    </div>"""
            res['arch'] = res['arch'].decode('utf8').replace(
                    """<separator string="to_replace"/>""", view_part)
            field = self.fields_get(cr, uid, [field_name], context=context)
            res_fields.update(field)
            res['fields'] = res_fields
            res['fields'][field_name]['domain'] = [('id', 'in', object_ids)]
            res['fields'][field_name]['required'] = True
        return res

    @api.multi
    def action_merge(self):
        """
        Merges two (or more objects
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Lead to Opportunity IDs
        @param context: A standard dictionary for contextual values

        @return : {}
        """
        assert len(self) == 1
        
        active_model = self.env.context.get('active_model')
        if not active_model:
            raise except_orm(_('Configuration Error!'),
                             _('The is no active model defined!'))
        model_pool = self.env[active_model]
        objects = model_pool.search([('id', 'in', self.env.context.get('active_ids',[]))])
        field_to_read = self.env.context.get('field_to_read')
        
        object = self[field_to_read]
        if not object:
            raise except_orm(_('Configuration Error!'),
                             _('Please select one value to keep'))
        tfields = self.env['ir.model.fields'].search([('relation', '=', active_model), ('ttype', 'not in', ['one2many', 'many2many'])])
        for field in tfields:
            model_raw_obj = self.env[field.model]
            if hasattr(model_raw_obj, '_auto'):
                if not model_raw_obj._auto:
                    continue
            if hasattr(model_raw_obj, '_check_time'):
                continue
            else:
                if hasattr(model_raw_obj, '_columns'):
                    
                    if model_raw_obj._columns.get(field.name, False) and \
                            (isinstance(model_raw_obj._columns[field.name],
                                        old_fields.many2one) \
                            or isinstance(model_raw_obj._columns[field.name],
                                          old_fields.function) \
                            and model_raw_obj._columns[field.name].store):
                        
                        #If the field is readonly, directly update in the database.
                        #Otherwise use normal methods so we trigger recalculation of computed fields
                        if model_raw_obj._columns[field.name].readonly:
                            if hasattr(model_raw_obj, '_table'):
                                model = model_raw_obj._table
                            else:
                                model = model_raw.replace('.', '_')
                            requete = "UPDATE %s SET %s = %s WHERE " \
                                "%s IN %s;" % (model, field.name, str(object.id),
                                               ustr(field.name), str(tuple(objects.mapped('id'))))
                            self.env.cr.execute(requete)
                        else:
                            records_to_change = model_raw_obj.sudo().search([(field.name, 'in', objects.mapped('id'))])
                            records_to_change.write({field.name: object.id})
        
        tfields = self.env['ir.model.fields'].search([('relation', '=', active_model), ('ttype', '=', 'many2many')])
        for field in tfields:
            model_obj = self.env[field.model]
            
            if (not isinstance(model_obj._fields[field.name], fields.Many2many)
                or not model_obj._fields[field.name].store):
                continue
             
            model_m2m, rel1, rel2 = model_obj._fields[field.name].to_column()._sql_names(model_obj)
            
            #Fix: relations might be wrong if the model inherits another model with a m2m field,
            #defines its own _name and the inherited model has a relation_table set in the m2m field
            #So we retrieve a list of columns from the given table and check if all required columns
            #exist in the database. Example: mail.compose.message, field needaction_partner_ids
            self.env.cr.execute("SELECT * FROM %s LIMIT 0" % model_m2m)
            table_fields = [f.name for f in self.env.cr.description]
            
            if rel1 in table_fields and rel2 in table_fields:
                
                requete = "UPDATE %s SET %s=%s WHERE %s " \
                    "IN %s AND %s NOT IN (SELECT DISTINCT(%s) " \
                    "FROM %s WHERE %s = %s);" % (model_m2m, rel2,
                                                 str(object.id),
                                                 ustr(rel2),
                                                 str(tuple(objects.mapped('id'))),
                                                 rel1, rel1, model_m2m,
                                                 rel2, str(object.id))
                self.env.cr.execute(requete)
            else:
                _logger.warn("Table %s: field %s or %s not existing." % (model_m2m, rel1, rel2))
                    
        tfields = self.env['ir.model.fields'].search([('name', 'in', ['model', 'res_model'])])
        for field in tfields:
            model_obj = self.env[field.model]
            if not model_obj:
                continue
            if field.name == 'model' and model_obj._columns.get('res_model', False):
                continue
            res_id = model_obj._columns.get('res_id')
            if res_id:
                requete = False
                if isinstance(res_id, old_fields.integer) or \
                        isinstance(res_id, old_fields.many2one):
                    requete = "UPDATE %s SET res_id = %s " \
                    "WHERE res_id IN %s AND " \
                    "%s = '%s';" % (model_obj._table,
                                    str(object.id),
                                    str(tuple(objects.mapped('id'))),
                                    field.name,
                                    active_model)
                elif isinstance(res_id, old_fields.char):
                    requete = "UPDATE %s SET res_id = '%s' " \
                    "WHERE res_id IN %s AND " \
                    "%s = '%s';" % (model_obj._table,
                                    str(object.id),
                                    str(tuple([str(x) for x in objects.mapped('id')])),
                                    field.name,
                                    active_model)
                if requete:
                    self.env.cr.execute(requete)
        inactive_objects = model_pool.search([
                             ('id', 'in', objects.mapped('id')),
                             ('id', '<>', object.id),
                             ])
        if model_pool._columns.get('active', False):
            inactive_objects.write({'active': False})
        else:
            if self.delete_if_not_active:
                inactive_objects.unlink()
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
