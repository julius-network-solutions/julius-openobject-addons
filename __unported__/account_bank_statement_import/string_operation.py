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

import time
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

def str2date(date_str, date_format="%d%m%y"):
    import locale
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    date_formated = datetime.strptime(date_str, date_format)
    return date_formated.strftime(DF)

def to_unicode(s):
   try:
       return s.decode('utf-8')
   except UnicodeError:
       try:
           return s.decode('latin')
       except UnicodeError:
           try:
               return s.encode('ascii')
           except UnicodeError:
               return s

def str2float(float_str, separator=None):
     try:
         float_str = float_str.replace('"','')
         if separator:
             float_str = float_str.replace(separator, '.')
         return float(float_str)
     except:
         return 0.0

def get_key_from_date(date_str, date_format):
    import locale
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    date_formated = datetime.strptime(date_str, date_format)
    return time.strftime('%Y-%m', time.strptime(date_str, date_format))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
