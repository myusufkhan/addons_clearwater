# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductExtended(models.Model):
    _inherit = 'product.template'
    is_equipment = fields.Boolean(string="Is Equipment")
