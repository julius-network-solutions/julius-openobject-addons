# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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

from osv import fields, osv
from tools.translate import _

class project_work(osv.osv):
    _inherit = "project.task.work"
    _columns = {
        'project_id': fields.related('task_id', 'project_id', string='Project', type='many2one', relation='project.project', readonly=True),
    }
    
#    def write(self, cr, uid, ids, vals, context=None):
#        if not 'user_id' in vals:
#            vals.update({'user_id': uid})  
    
        
project_work()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

