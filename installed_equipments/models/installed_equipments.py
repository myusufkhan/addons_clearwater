# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMoveDatesExtend(models.Model):
    _inherit = "stock.move.dates"

    is_equipment = fields.Boolean(string="Is Equipment",compute="_compute_product")
    delivery_date = fields.Date(string="Delivery Date",compute="_compute_product")
    state = fields.Selection([
        ('draft', 'draft'),
        ('in_use', 'In Use'),
        ('removed', 'Removed'),
        ],
        string='Status',
        copy=False, default='draft', readonly=True, required=True)

    def action_remove(self):
        self.state = 'removed'


    @api.depends('product_id')
    def _compute_product(self):
        for rec in self:
            # print(rec.picking_id.name)
            if rec.product_id.is_equipment:
                rec.is_equipment = rec.product_id.is_equipment
            else:
                rec.is_equipment = False
            print("state",rec.state)
            if rec.state !='removed':
                if rec.picking_id.state == 'done':
                    rec.state = 'in_use'
            rec.write({'delivery_date': rec.picking_id.date_done})

