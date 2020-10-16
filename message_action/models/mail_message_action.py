# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developped by 
# Copyright (c) 2020-Today Julius Network Solutions
# (http://www.julius.fr) All Rights Reserved.

from odoo import api, fields, models, _


class MailMessageAction(models.Model):
    _name = "mail.message.action"
    _description = "Mail Message Actions"

    name = fields.Char()
    value = fields.Text("Tested Value", required=True)
    model_id = fields.Many2one("ir.model", required=True)
    model_name = fields.Char(related="model_id.model", readonly=True,
                             store=True)
    user_id = fields.Many2one("res.users")
    action = fields.Selection([
                               ("create_move", "Create Move"),
                               ], default="create_move", required=True)
    location_id = fields.Many2one("stock.location",
                                  "Location")
    origin = fields.Char()
    keep_in_package = fields.Boolean(default=False)

    def do_action(self, message):
        if self.action == "create_move":
            if self.user_id:
                self = self.with_user(self.user_id)
            picking = self.env["stock.picking"]
            move = self.env["stock.move"]
            move_line = self.env["stock.move.line"]
            quant = self.env["stock.quant"]
            prodlot = self.env[message.model].browse(message.res_id)
            if not prodlot:
                return "Production lot not found"
            quant = quant.\
                search([
                        ("lot_id", "=", prodlot.id),
                        ("quantity", "=", 1),
                        ], limit=1)
            if not quant:
                return "Production lot not located"
            try:
                type_id = self.env.ref("stock.picking_type_internal").id
                vals = {
                        "picking_type_id": type_id,
                        "location_id": quant.location_id.id,
                        "location_dest_id": self.location_id.id,
                        }
                if self.origin:
                    vals.update({"origin": self.origin})
                picking = picking.create(vals)
                move = move.create({
                                    "picking_id": picking.id,
                                    "name": self.name,
                                    "product_id": prodlot.product_id.id,
                                    "product_uom_qty": prodlot.product_qty,
                                    "product_uom": prodlot.product_uom_id.id,
                                    "location_id": quant.location_id.id,
                                    "location_dest_id": self.location_id.id,
                                    "date": message.date,
                                    "company_id": self.env.company.id,
                                    })
                picking.action_confirm()
                picking.action_assign()
                vals = {
                        "lot_id": prodlot.id,
                        "lot_name": prodlot.name,
                        "qty_done": prodlot.product_qty,
                        "package_id": quant.package_id.id,
                        "result_package_id": False,
                        }
                if self.origin:
                    vals.update({"origin": self.origin})
                if self.keep_in_package:
                    vals.update({"result_package_id": quant.package_id.id})
                move.move_line_ids.write(vals)
                picking.button_validate()
#                 move_line = move_line.\
#                     create({
#                             "move_id": move.id,
#                             "picking_id": picking.id,
#                             "product_id": prodlot.product_id.id,
#                             "product_uom_qty": prodlot.product_qty,
#                             "product_uom_id": prodlot.product_uom_id.id,
#                             "lot_id": prodlot.id,
#                             "lot_name": prodlot.name,
#                             "location_id": quant.location_id.id,
#                             "location_dest_id": self.location_id.id,
#                             "date": message.date,
#                             "company_id": self.env.company.id,
#                             })
#                 picking.action_confirm()
#                 picking.action_assign()
#                 picking.button_validate()
#                 move_line._action_done()
            except Exception as e:
                return e

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
