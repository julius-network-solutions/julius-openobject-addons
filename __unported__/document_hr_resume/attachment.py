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

from openerp import models, fields, api


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    is_resume = fields.Boolean('Is a resume', default=False)


class document_resumes(models.AbstractModel):
    _name = 'document.resumes'
    _description = 'Attachment Resumes'
    
    resume_ids = fields.One2many('ir.attachment', string='Resumes',
                                compute='_get_resumes')

    @api.model
    def _get_resumes_from_attachment(self, res_id, domain=None):
        attachment_obj = self.env['ir.attachment']
        domain += [
                   ('res_id', '=', res_id),
                   ('res_model', '=', self._name),
                   ('is_resume', '=', True),
                   ]
        return attachment_obj.search(domain, order='create_date DESC')

    @api.one
    def _get_resumes(self):
        self.resume_ids = self._get_resumes_from_attachment(self.id, domain=[])

    resume_id = fields.Many2one('ir.attachment', string='Last resume',
                                compute='_get_last_resume')

    @api.one
    def _get_last_resume(self):
        self.resume_id = self.resume_ids and self.resume_ids[0]

    resume_data = fields.Binary('Resume', compute='_get_last_resume_data', store=False)

    @api.one
    def _get_last_resume_data(self):
        value = self.resume_id.datas
        self.resume_data = value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
