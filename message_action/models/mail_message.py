# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developped by 
# Copyright (c) 2020-Today Julius Network Solutions
# (http://www.julius.fr) All Rights Reserved.

from odoo import api, fields, models, _, exceptions
from odoo.tools.mail import html2plaintext
import logging

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"

    to_be_treated = fields.Boolean(default=False)

    def treat_message(self):
        message = self.body
        try:
            text_message = html2plaintext(message)
        except Exception as e:
            text_message = message
            _logger.warning(str(e))
            if self._context.get("raise_on_error", False):
                raise exceptions.Warning(e)
        message_action = self.env["mail.message.action"]
        actions = message_action.\
            search([
                    ("model_name", "=", self.model),
                    ])
        action = actions.filtered(lambda a: text_message == a.value)
        if action:
            error = action.do_action(self)
            if error:
                # log error here
                _logger.warning(error)
                if self._context.get("raise_on_error", False):
                    raise exceptions.Warning(error)
                return
            self.to_be_treated = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
