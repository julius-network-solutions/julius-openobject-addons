# -*- encoding: latin-1 -*-
##############################################################################
#
# Copyright (c) 2011 Julius Network Solutions SARL, 
# NaN Projectes de Programari Lliure, S.L. All Rights Reserved.
#                    http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name" : "Account Invoice Sequence Writeable",
    "version" : "1.0",
    "author" : "NaN, Julius",
    "category" : "Accounting & Finance",
    "website": "http://www.NaN-tic.com",
    "description": """\
This module separates invoice and account move numbers. The difference with account_sequence module is that instead of creating a new internal number in moves which would require changing lots of reports, it simply converts invoice's number related field into a normal char one.
""",
    "depends" : [
        'account',
	],
    "demo" : [],
    "data" : [
        'account_view.xml',
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
