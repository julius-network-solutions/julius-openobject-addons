# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developped by 
# Copyright (c) 2020-Today Julius Network Solutions
# (http://www.julius.fr) All Rights Reserved.

from odoo import api, models, _


class StockTraceabilityReport(models.TransientModel):
    _inherit = "stock.traceability.report"

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        """
        I"m doing this sorted here and not in the get_lines
        method because it"s more easier to inherit here.
        If I"ve done it in the other method I should have
        rewritten the complete method.
        This is done only to sort data with ID if the record
        has been created the same second.
        """
        final_vals = sorted(final_vals,
                            key=lambda v: (v["date"], v["model_id"]),
                            reverse=True)
        return super(StockTraceabilityReport, self).\
            _final_vals_to_lines(final_vals, level)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
