# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, fields

class crm_heard_about_us(models.Model):
    _name = 'crm.hear.about.us'
    _description = 'How did the customer hear about us'
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char(translate=True, required=True)

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    hear_about_us_id = fields.Many2one('crm.hear.about.us',
                                       'How did the customer hear about us ?')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
