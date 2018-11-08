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

import time
import operator
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class EasyExport(models.TransientModel):
    _name = 'easy.export'
    _description = 'Wizard to export easily data from filtered values'

    model_id = fields.Many2one('ir.model', 'Model to export',
                               required=True)
    name = fields.Char('Model name', related='model_id.model',
                       readonly=True, store=True)
    export_id = fields.Many2one('ir.exports', 'Export',
                                domain="[('resource', '=', name)]",
                                required=True)
    import_compat = fields.Boolean("Import compatible",
                                   default=False)
    export_active_ids = fields.Boolean("Export selected records",
                                       default=False)
    export_domain = fields.Char(compute='compute_active_domain')

    @api.onchange('model_id')
    def onchange_model_id(self):
        export = self.env['ir.exports'].\
            search([
                    ('default_easy_export', '=', True),
                    ('resource', '=', self.model_id.model),
                    ], limit=1)
        self.export_id = export.id

    @api.one
    def compute_active_domain(self):
        self.export_domain = []

    @api.multi
    def get_data(self, ids=[]):
        self.ensure_one()
        model = self.name
        fields = [field for field in self.export_id.export_fields if field['name'] != 'id']
        field_names = map(operator.itemgetter('name'), fields)
        if self.import_compat:
            columns_headers = field_names
        else:
            columns_headers = map(operator.itemgetter('column_label'), fields)
        field_data = '['
        fields_data = []
        i = 0
        for field in field_names:
            field_name = field
            field_label = columns_headers[i] or field
            fields_data.append('{"name": "%s", "label": "%s"}' % (field_name, field_label))
            i += 1
        field_data += ','.join(fields_data)
        field_data += ']'
        context = '{"lang": "%s", "tz": "%s", "uid": %s, ' \
            '"active_test": false}' % (self._context.get('lang', "en_US"),
                                       self._context.get('tz', "Europe/Paris"),
                                       self._context.get('uid', self._uid))
        import_compat = self.import_compat is True and 'true' or 'false'
        data = '{"model": "%s", "fields": %s, "ids": %s, "domain": [], \
            "context": %s, "import_compat": %s}' % (model, field_data, ids,
                                                    context, import_compat)
        return data

    @api.multi
    def get_ids(self, domain):
        ids = False
        if self.export_active_ids:
            ids = self._context.get('active_ids')
        if not ids:
            ids = self.env[self.name].search(eval(domain)).ids
            ids = ids and str(ids) or False
            if not ids:
                raise Warning(_("Nothing to export."))
        return ids

    @api.multi
    def export_file_xls(self):
        self.ensure_one()
        token = int(time.time())
        ids = self.get_ids(self.export_domain)
        data = self.get_data(ids)
        return {
                'type' : 'ir.actions.act_url',
                'url': '/web/export/xls?data=%s&token=%s' %(data, token),
                'target': 'self',
                }

    @api.model
    def get_xml_value(self):
        return ''

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        res = super(EasyExport, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=False)
        xml_value = self.get_xml_value()
        res['arch'] = unicode(res['arch'], 'utf8').\
            replace('<separator string="to_replace"/>', xml_value)
        xarch, xfields = self.env['ir.ui.view'].\
            postprocess_and_fields(self._name, etree.fromstring(res['arch']),
                                   view_id)
#         res['arch'] = xarch
        res['fields'] = xfields
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
