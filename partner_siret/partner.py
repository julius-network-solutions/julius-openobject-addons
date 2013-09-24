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

from osv import fields, orm
from tools.translate import _

class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    _columns = {
        'siret':  fields.char('Siret', size=16),
    }
    
class crm_lead(orm.Model):
    _inherit = 'crm.lead'
    
    _columns = {
        'siret':  fields.char('Siret', size=16),
    }
    
    def on_change_partner(self, cr, uid, ids, partner_id, context=None):
        result =  super(crm_lead, self).on_change_partner(cr, uid, ids, partner_id=partner_id, context=context)
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            result['value'].update({'siret': partner.siret})
        return result
    
    def _convert_opportunity_data(self, cr, uid, lead, customer, section_id=False, context=None):
        val = super(crm_lead, self)._convert_opportunity_data(cr, uid, lead=lead, customer=customer, section_id=section_id, context=context)
        val.update({'siret': lead.siret})
        return val
    
    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        partner_id = super(crm_lead, self)._lead_create_contact(cr, uid, lead=lead, name=name, is_company=is_company, parent_id=parent_id, context=context)
        partner = self.pool.get('res.partner')
        vals = {
            'siret': lead.siret,
        }
        partner.write(cr, uid, [partner_id], vals, context=context)
        return partner_id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
