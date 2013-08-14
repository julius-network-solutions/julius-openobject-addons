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

class partner_merger(orm.TransientModel):
    '''
    Merges partners
    '''
    _name = 'partner.merger'
    _description = 'Merge partners'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner to keep', required=True),
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(partner_merger, self).fields_view_get(cr, uid, view_id, view_type,
                                    context=context, toolbar=toolbar, submenu=False)
        partner_ids = context.get('active_ids',[])
        if partner_ids:
            view_part = '<field name="partner_id" widget="selection" domain="[(\'id\', \'in\', ' + str(partner_ids) + ')]"/>'
            res['arch'] = res['arch'].decode('utf8').replace('<field name="partner_id"/>', view_part)
            res['fields']['partner_id']['domain'] = [('id', 'in', partner_ids)]
        return res

    def action_merge(self, cr, uid, ids, context=None):
        """
        Merges two partner
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

#        res.update(self._values)
        partner_pool = self.pool.get('res.partner')
        partner_ids = context.get('active_ids',[])
        partner_id = self.browse(cr, uid, ids, context=context)[0].partner_id.id
        # For one2many fields on res.partner
        cr.execute("select name, model from ir_model_fields where relation='res.partner' and ttype not in ('many2many', 'one2many');")
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
                        requete = "UPDATE "+model+" SET "+name+"="+str(partner_id)+" WHERE "+ ustr(name) +" IN " + str(tuple(partner_ids)) + ";"
                        cr.execute(requete)
        cr.execute("select name, model from ir_model_fields where relation='res.partner' and ttype in ('many2many');")
        for field, model in cr.fetchall():
            field_data = self.pool.get(model) and self.pool.get(model)._columns.get(field, False) \
                            and (isinstance(self.pool.get(model)._columns[field], fields.many2many) \
                            or isinstance(self.pool.get(model)._columns[field], fields.function) \
                            and self.pool.get(model)._columns[field].store) \
                            and self.pool.get(model)._columns[field] \
                            or False
            if field_data:
                model_m2m, rel1, rel2 = field_data._sql_names(self.pool.get(model))
                requete = "UPDATE "+model_m2m+" SET "+rel2+"="+str(partner_id)+" WHERE "+ ustr(rel2) +" IN " + str(tuple(partner_ids)) + ";"
                cr.execute(requete)
        unactive_partner_ids = partner_pool.search(cr, uid, [('id', 'in', partner_ids), ('id', '<>', partner_id)], context=context)
        partner_pool.write(cr, uid, unactive_partner_ids, {'active': False}, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
