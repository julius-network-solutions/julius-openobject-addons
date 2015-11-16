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

from openerp import fields, models, api
    
class crm_lead(models.Model):
    _inherit = 'crm.lead'
    
    siret = fields.Char('Siret', size=16)
    
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        result =  super(crm_lead, self).\
            on_change_partner_id(cr, uid, ids, partner_id=partner_id,
                                 context=context)
        if not 'value' in result.keys():
            result['value'] = {}
        if partner_id:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, uid, partner_id, context=context)
            result['value'].update({
                                    'siret': partner.siret,
                                    })
        return result

    @api.model
    def _convert_opportunity_data(self, lead, customer, section_id=False):
        vals = super(crm_lead, self).\
            _convert_opportunity_data(lead=lead, customer=customer,
                                      section_id=section_id)
        vals.update({
                     'siret': lead.siret,
                     })
        return vals

    @api.model
    def _lead_create_contact(self, lead, name, is_company, parent_id=False):
        partner_id = super(crm_lead, self).\
            _lead_create_contact(lead=lead, name=name,
                                 is_company=is_company, parent_id=parent_id)
        vals = {
            'siret': lead.siret,
        }
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(partner_id)
        partner.write(vals)
        return partner_id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
