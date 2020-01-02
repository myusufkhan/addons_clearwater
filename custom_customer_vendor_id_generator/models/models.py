# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Vendor_customer_id_field(models.Model):
	_inherit = 'res.partner'

	customer_id = fields.Char(string="Account ID", readonly=False, required=False)
	town_ship = fields.Char(string="Town Ship")
	@api.model
	def create(self, data):

		# sequence = self.env['ir.sequence']

		# prefix = data['name'][:1].upper()
		# sequence = self.env['ir.sequence'].search([('code','=','res.partner.customer')])
		# if not sequence:
		# 	padding = 4
		# 	implementation='no_gap'
		# 	active=True
		# 	sequence = self.env['ir.sequence'].create({'padding':padding,'implementation':implementation,'active':active, 'name':'Customer Id '+prefix,'code':'res.partner.customer'})
		# add type check dont create sequence if contact is comapanay
		if data['parent_id'] == False:
			data['customer_id'] = self.env['ir.sequence'].next_by_code('res.partner.customer') or ''

		return super(Vendor_customer_id_field, self).create(data)

	# def write(self, vals):
	#
	# 	if 'customer_id' in vals.keys():
	# 		# prefix = self['name'][:1].upper()
	# 		# sequence = self.env['ir.sequence'].search([('code','=','res.partner.customer')])
	# 		# if not sequence:
	# 			# padding = 4
	# 			# implementation='no_gap'
	# 			# active=True
	# 			# sequence = self.env['ir.sequence'].create({'padding':padding,'implementation':implementation,'active':active, 'name':'Customer Id '+prefix,'code':'res.partner.customer'})
	# 		vals['customer_id'] = self.env['ir.sequence'].next_by_code('res.partner.customer') or '',
	#
	#
	#
	# 	return super(Vendor_customer_id_field, self).write(vals)
