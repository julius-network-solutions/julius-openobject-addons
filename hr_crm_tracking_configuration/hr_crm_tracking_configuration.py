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


#V8
from openerp.osv import osv
from openerp.osv import fields

class configurable_fields_setting(osv.osv):
    "Specific Fields For FHM"
    _name = 'configurable.fields.setting'
    _description = "Configurable Field"
    _columns = {
                'name': fields.char('Field', size=64),                
                'type': fields.selection([('hr','Human Resources'),
                                          ('commercial','Commercial'),
                                          ('hr_commercial','Human Resources or Commercial')],'Type'),                
    }
configurable_fields_setting()

class configurable_fields(osv.osv):
    "Specific Fields For FHM"
    _name = 'configurable.fields'
    _description = "Configurable Field"    
    _columns = {
                'name': fields.char('Name', size=64),
                'field': fields.many2one('configurable.fields.setting', 'Category'),
    }
configurable_fields()

class characteristic(osv.osv):
     _name = 'characteristic'
     _description = "Characteristic"
     _columns = {
                 'name':fields.char('Category Name', size=64, required=True),
                 'type_id':fields.many2one('characteristic', 'Domain'),
    }
characteristic()

class characteristic_type(osv.osv):
     _name = 'characteristic.type'
     _description = "Characteristic Type"
     _columns = {
                 'name':fields.char('Name', size=64),
                 'parent_id':fields.many2one('characteristic', 'Parent'),
    }
characteristic_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
