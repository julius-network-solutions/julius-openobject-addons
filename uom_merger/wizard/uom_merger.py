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
from osv import fields, orm
from tools.translate import _
import tools

class uom_merger(orm.TransientModel):
    '''
    Merges uom
    '''
    _name = 'uom.merger'
    _description = 'Merges uom'

    _columns = {
        'uom_id': fields.many2one('product.uom', 'Uom to keep', required=True),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False,submenu=False):
        if context is None:
            context = {}
        res = super(uom_merger, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar,submenu=False)
        uom_ids = context.get('active_ids',[])
        if uom_ids:
            view_part = '<field name="uom_id" widget="selection" domain="[(\'id\', \'in\', ' + str(uom_ids) + ')]"/>'
            res['arch'] = res['arch'].decode('utf8').replace('<field name="uom_id"/>', view_part)
            res['fields']['uom_id']['domain'] = [('id', 'in', uom_ids)]
        return res

    def action_merge(self, cr, uid, ids, context=None):
        """
        Merges two uom
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Lead to Opportunity IDs
        @param context: A standard dictionary for contextual values

        @return : {}
        """
        if context is None:
            context = {}
        res = self.read(cr, uid, ids, context = context)[0]

#        res.update(self._values)
        uom_pool = self.pool.get('product.uom')
        uom_ids = context.get('active_ids',[])
        uom_id = self.browse(cr, uid, ids, context=context)[0].uom_id.id
        # For one2many fields on res.partner
        cr.execute("select name, model from ir_model_fields where relation='product.uom' and ttype not in ('many2many', 'one2many');")
        for name, model_raw in cr.fetchall():
            if hasattr(self.pool.get(model_raw), '_auto'):
                if not self.pool.get(model_raw)._auto:
                    continue
            if hasattr(self.pool.get(model_raw), '_check_time'):
                continue
            else:
                if hasattr(self.pool.get(model_raw), '_columns'):
                    from osv import fields
                    if self.pool.get(model_raw)._columns.get(name, False) and isinstance(self.pool.get(model_raw)._columns[name], fields.many2one):
                        model = model_raw.replace('.', '_')
                        requete = "update "+model+" set "+name+"="+str(uom_id)+" where "+ tools.ustr(name) +" in " + str(tuple(uom_ids)) + ";"
                        cr.execute(requete)
#        print """ ================================= """
#        cr.execute("select name, model from ir_model_fields where relation='res.users' and ttype in ('many2many');")
#        for field, model in cr.fetchall():
#            print model, field
        unactive_uom_ids = uom_pool.search(cr, uid, [('id', 'in', uom_ids), ('id', '<>', uom_id)])
        uom_pool.write(cr, uid, unactive_uom_ids, {'active': False})
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
