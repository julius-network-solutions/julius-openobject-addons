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

from email.utils import formataddr
from openerp import models


class mail_mail(models.Model):
    _inherit = 'mail.mail'

    def send_get_mail_to(self, cr, uid, mail, partner=None, context=None):
        """Forge the email_to with the following heuristic:
          - if 'partner', recipient specific (Partner Name <email>)
          - else fallback on mail.email_to splitting """
        if not partner:
            return super(mail_mail, self).\
                send_get_mail_to(cr, uid, mail,
                                 partner=partner, context=context)
        else:
            emails = partner.email.split(';')
            email_to = []
            for email in emails:
                email_to.append(formataddr((partner.name, email)))
        return email_to

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
