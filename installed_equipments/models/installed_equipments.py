# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveDatesExtend(models.Model):
        _inherit = "stock.move.dates"

        old_state = fields.Char()
        is_equipment = fields.Boolean(string="Is Equipment", compute="_compute_product")
        delivery_date = fields.Date(string="Delivery Date")


        state = fields.Selection([
            ('draft', 'draft'),
            ('in_use', 'In Use'),
            ('removed', 'Removed'),
        ],
            string='Status',
            compute="_compute_state", store=True, default='draft')




        def action_remove(self):
            self.state = 'removed'

        @api.depends('picking_id.state','old_state')
        def _compute_state(self):
            for rec in self:
                if rec.old_state:
                    rec.write({'state': rec.old_state})
                else:
                    if rec.picking_id.id:
                        if rec.state != 'removed':
                            if rec.picking_id.state == 'done':
                                rec.write({'state': 'in_use'})



        @api.depends('product_id')
        def _compute_product(self):
            for rec in self:
                # print(rec.picking_id.name)
                if rec.product_id.is_equipment:
                    rec.is_equipment = rec.product_id.is_equipment
                else:
                    rec.is_equipment = False

                rec.write({'delivery_date': rec.picking_id.date_done})
