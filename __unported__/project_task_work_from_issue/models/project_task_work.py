# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-Today Julius Network Solutions SARL <contact@julius.fr>
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

import re

from openerp import models, api
from openerp.tools.safe_eval import safe_eval as eval


class project_task_work(models.Model):
    _inherit = "project.task.work"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(project_task_work, self).\
            fields_view_get(cr, uid, view_id, view_type,
                            context, toolbar, submenu)
        try:
            if 'name="task_id"' in res["arch"] and context.get('domain_task'):
                task_id_re = re.search('<field.*\"task_id\".*/>', res["arch"])
                task_id_str = task_id_re.group(0)
                project_id = context.get('domain_task')
                if "domain" in task_id_str:
                        domain_re = re.search('domain=\"\[(.*)]\"', task_id_str)
                        domain_str = "[" + domain_re.group(1) + "]"
                        domain = eval(domain_str)
                        domain.extend([('project_id', '=', project_id)])
                        str_replace = task_id_str.\
                            replace('domain="%s"' % domain_str,
                                    'domain="%s"' % domain)
                        print str_replace
                else:
                    domain = "[('poject_id, '=', %s)]" % project_id
                    str_replace = task_id_str.\
                        replace('"task_id"',
                                '"task_id" domain="%s"' % domain)
                arch = res["arch"].replace(task_id_str, str_replace)
                res["arch"] = arch
        except:
            pass
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
