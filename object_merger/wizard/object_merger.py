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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import ustr

class object_merger(orm.TransientModel):
    '''
    Merges partners
    '''
    _name = 'object.merger'
    _description = 'Merge objects'

    _columns = {
        'name': fields.char('Name', size=16),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(object_merger, self).fields_view_get(cr, uid, view_id, view_type,
                                    context=context, toolbar=toolbar, submenu=False)
        object_ids = context.get('active_ids',[])
        active_model = context.get('active_model')
        field_name = 'x_' + (active_model and active_model.replace('.','_') or '') + '_id'
        if object_ids:
            view_part = """<label for='"""+field_name+"""'/>
                        <div>
                            <field name='""" + field_name +"""' required="1" domain="[(\'id\', \'in\', """ + str(object_ids) + """)]"/>
                        </div>"""
#                            <field name='""" + field_name +"""' domain="[(\'id\', \'in\', '""" + str(object_ids) + """')]"/>'
            res['arch'] = res['arch'].decode('utf8').replace(
                    """<separator string="to_replace"/>""", view_part)
            field = self.fields_get(cr, uid, [field_name], context=context)
            res['fields'] = field
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
            raise orm.except_orm(_('Configuration Error!'),
                 _('The is no active model defined!'))
        model_pool = self.pool.get(active_model)
        object_ids = context.get('active_ids',[])
        field_to_read = context.get('field_to_read')
        fields = field_to_read and [field_to_read] or []
        object = self.read(cr, uid, ids[0], fields, context=context)
        if object and fields and object[field_to_read]:
            object_id = object[field_to_read][0]
        else:
            raise orm.except_orm(_('Configuration Error!'),
                 _('Please select one value to keep'))
        # For one2many fields on res.partner
        cr.execute("SELECT name, model FROM ir_model_fields WHERE relation=%s and ttype not in ('many2many', 'one2many');", (active_model, ))
        for name, model_raw in cr.fetchall():
            if hasattr(self.pool.get(model_raw), '_auto'):
                if not self.pool.get(model_raw)._auto:
                    continue
            if hasattr(self.pool.get(model_raw), '_check_time'):
                continue
            else:
                if hasattr(self.pool.get(model_raw), '_columns'):
                    from osv import fields
                    if self.pool.get(model_raw)._columns.get(name, False) and \
                            (isinstance(self.pool.get(model_raw)._columns[name], fields.many2one) \
                            or isinstance(self.pool.get(model_raw)._columns[name], fields.function) \
                            and self.pool.get(model_raw)._columns[name].store):
                        if hasattr(self.pool.get(model_raw), '_table'):
                            model = self.pool.get(model_raw)._table
                        else:
                            model = model_raw.replace('.', '_')
                        requete = "UPDATE "+model+" SET "+name+"="+str(object_id)+" WHERE "+ ustr(name) +" IN " + str(tuple(object_ids)) + ";"
                        cr.execute(requete)
        cr.execute("select name, model from ir_model_fields where relation=%s and ttype in ('many2many');", (active_model, ))
        for field, model in cr.fetchall():
            field_data = self.pool.get(model) and self.pool.get(model)._columns.get(field, False) \
                            and (isinstance(self.pool.get(model)._columns[field], fields.many2many) \
                            or isinstance(self.pool.get(model)._columns[field], fields.function) \
                            and self.pool.get(model)._columns[field].store) \
                            and self.pool.get(model)._columns[field] \
                            or False
            if field_data:
                model_m2m, rel1, rel2 = field_data._sql_names(self.pool.get(model))
                requete = "UPDATE "+model_m2m+" SET "+rel2+"="+str(object_id)+" WHERE "+ ustr(rel2) +" IN " + str(tuple(object_ids)) + ";"
                cr.execute(requete)
        unactive_object_ids = model_pool.search(cr, uid, [('id', 'in', object_ids), ('id', '<>', object_id)], context=context)
        model_pool.write(cr, uid, unactive_object_ids, {'active': False}, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
