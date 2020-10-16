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
from openerp import models, fields, _
from openerp.exceptions import except_orm


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

    def action_merge(self, cr, uid, ids, context=None):
        """
        Merges two (or more objects
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Lead to Opportunity IDs
        @param context: A standard dictionary for contextual values

        @return : {}
        """
        if context is None:
            context = {}
        res = self.read(cr, uid, ids, context=context)[0]
        active_model = context.get('active_model')
        if not active_model:
            raise except_orm(_('Configuration Error!'),
                             _('The is no active model defined!'))
        model_pool = self.pool.get(active_model)
        object_ids = context.get('active_ids',[])
        field_to_read = context.get('field_to_read')
        field_list = field_to_read and [field_to_read] or []
        object = self.read(cr, uid, ids[0], field_list, context=context)
        if object and field_list and object[field_to_read]:
            object_id = object[field_to_read][0]
        else:
            raise except_orm(_('Configuration Error!'),
                             _('Please select one value to keep'))
        cr.execute("SELECT name, model FROM ir_model_fields WHERE relation=%s "
                   "and ttype not in ('many2many', 'one2many');", (active_model, ))
        for name, model_raw in cr.fetchall():
            if hasattr(self.pool.get(model_raw), '_auto'):
                if not self.pool.get(model_raw)._auto:
                    continue
            if hasattr(self.pool.get(model_raw), '_check_time'):
                continue
            else:
                if hasattr(self.pool.get(model_raw), '_columns'):
                    model_raw_obj = self.pool.get(model_raw)
                    if model_raw_obj._columns.get(name, False) and \
                            (isinstance(model_raw_obj._columns[name],
                                        old_fields.many2one) \
                            or isinstance(model_raw_obj._columns[name],
                                          old_fields.function) \
                            and model_raw_obj._columns[name].store):
                        if hasattr(self.pool.get(model_raw), '_table'):
                            model = self.pool.get(model_raw)._table
                        else:
                            model = model_raw.replace('.', '_')
                        requete = "UPDATE %s SET %s = %s WHERE " \
                            "%s IN %s;" % (model, name, str(object_id),
                                           ustr(name), str(tuple(object_ids)))
                        cr.execute(requete)
        cr.execute("SELECT name, model FROM ir_model_fields WHERE "
                   "relation=%s AND ttype IN ('many2many');", (active_model,))
        for field, model in cr.fetchall():
            model_obj = self.pool.get(model)
            if not model_obj:
                continue
            field_data = model_obj._columns.get(field, False) \
                            and (isinstance(model_obj._columns[field],
                                            old_fields.many2many) \
                            or isinstance(model_obj._columns[field],
                                          old_fields.function) \
                            and model_obj._columns[field].store) \
                            and model_obj._columns[field] \
                            or False
            if field_data:
                model_m2m, rel1, rel2 = field_data._sql_names(model_obj)
                requete = "UPDATE %s SET %s=%s WHERE %s " \
                    "IN %s AND %s NOT IN (SELECT DISTINCT(%s) " \
                    "FROM %s WHERE %s = %s);" % (model_m2m, rel2,
                                                 str(object_id),
                                                 ustr(rel2),
                                                 str(tuple(object_ids)),
                                                 rel1, rel1, model_m2m,
                                                 rel2, str(object_id))
                cr.execute(requete)
        cr.execute("SELECT name, model FROM ir_model_fields WHERE "
                   "name IN ('res_model', 'model');")
        for field, model in cr.fetchall():
            model_obj = self.pool.get(model)
            if not model_obj:
                continue
            if field == 'model' and model_obj._columns.get('res_model', False):
                continue
            res_id = model_obj._columns.get('res_id')
            if res_id:
                requete = False
                if isinstance(res_id, old_fields.integer) or \
                        isinstance(res_id, old_fields.many2one):
                    requete = "UPDATE %s SET res_id = %s " \
                    "WHERE res_id IN %s AND " \
                    "%s = '%s';" % (model_obj._table,
                                    str(object_id),
                                    str(tuple(object_ids)),
                                    field,
                                    active_model)
                elif isinstance(res_id, old_fields.char):
                    requete = "UPDATE %s SET res_id = '%s' " \
                    "WHERE res_id IN %s AND " \
                    "%s = '%s';" % (model_obj._table,
                                    str(object_id),
                                    str(tuple([str(x) for x in object_ids])),
                                    field,
                                    active_model)
                if requete:
                    cr.execute(requete)
        unactive_object_ids = model_pool.\
            search(cr, uid, [
                             ('id', 'in', object_ids),
                             ('id', '<>', object_id),
                             ], context=context)
        if model_pool._columns.get('active', False):
            model_pool.write(cr, uid, unactive_object_ids,
                             {'active': False}, context=context)
        else:
            read_data = self.read(cr, uid, ids[0],
                                  ['delete_if_not_active'], context=context)
            if read_data['delete_if_not_active']:
                model_pool.unlink(cr, uid,
                                  unactive_object_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
