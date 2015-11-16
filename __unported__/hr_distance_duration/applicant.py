# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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

from openerp.addons.google_maps_distance_duration.google_maps import GoogleMaps
from openerp.addons.base_geolocalize.models.res_partner import geo_query_address
import datetime
import time
from openerp import models, fields, api

class hr_applicant(models.Model):
    _inherit = 'hr.applicant'

    duration = fields.Float('Duration')
    distance = fields.Float('Distance')

    @api.one
    def get_distance_duration(self):
        duration = 0
        distance = 0
        departure_time = self._context.get('departure_time')
        if not departure_time:
            n = datetime.datetime.now()
            departure_time = int(time.mktime(n.timetuple()))
        if self.partner_id and self.job_id.address_id:
            partner = self.partner_id
            origin = geo_query_address(street=partner.street,
                                       zip=partner.zip,
                                       city=partner.city,
                                       state=partner.state_id.name,
                                       country=partner.country_id.name)
            partner = self.job_id.address_id
            destination = geo_query_address(street=partner.street,
                                            zip=partner.zip,
                                            city=partner.city,
                                            state=partner.state_id.name,
                                            country=partner.country_id.name)
            maps = GoogleMaps()
            duration = maps.duration(origin, destination, mode='transit',
                                     departure_time=departure_time) / 60.0
            distance = maps.distance(origin, destination, mode='transit',
                                     departure_time=departure_time) / 1000.0
        self.write({'duration': duration, 'distance': distance})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
