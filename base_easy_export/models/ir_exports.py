# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018-Today Julius Network Solutions SARL <contact@julius.fr>
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


class ir_exports(models.Model):
    _inherit = 'ir.exports'
 
    default_easy_export = fields.Boolean(default=False)


class IrExportsLine(models.Model):
    _inherit = 'ir.exports.line'
    column_label = fields.Char('Column label',
                               help="This field is use for " \
                               "the 'easy export' exports")


# class IrExportsFilters(models.Model):
#     _name = 'ir.exports.filters'
#     _description = 'Fields to filter data for easy export'
# 
#     field_id = fields.Many2one('ir.model.fields', 'Field to filter',
#                                required=True)
#     name = fields.Char('Name', related='field_id.name', readonly=True,
#                        store=True)
#     export_id = fields.Many2one('ir.exports', 'Export',
#                                 required=True)
#     arch = fields.Text(defaut="<field name='field_name'/>")
# 
#     @api.onchange('field_id')
#     def onchange_field_id(self):
#         if self.field_id and self.arch \
#                 and "<field name='field_name'/>" in self.arch:
#             arch = self.arch.replace('field_name', self.field_id.name)
#             self.arch = arch

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
