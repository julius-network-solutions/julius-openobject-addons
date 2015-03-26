# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.addons.web.controllers.main import Export
from openerp import http
try:
    import xlwt
except ImportError:
    xlwt = None

class ExportReversed(Export):

    @http.route('/web/export/formats', type='json', auth="user")
    def formats(self):
        res = super(ExportReversed, self).formats()
        result = [{
                   'tag': 'xls', 'label': 'Excel',
                   'error': None if xlwt else "XLWT required"
                  }]
        for dictionary in res:
            if dictionary.get('tag') == 'xls':
                continue
            result.append(dictionary)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
