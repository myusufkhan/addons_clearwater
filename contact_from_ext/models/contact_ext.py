# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class ResPartnerExtended(models.Model):
	_inherit = 'res.partner'

	#
	rental_count = fields.Integer(compute='_voucher_count', string='Partners Count' )
	rental_ids = fields.One2many('sale.order', 'partner_id') # Many2many


	def _voucher_count(self):
		vouchers = self.env['sale.order'].search([('partner_id', '=', self.id),('rental_status', '!=', False)])
		self.rental_count = len(vouchers)


	def action_create_rentals(self):
		rental = self.mapped('rental_ids')
		action = self.env.ref('sale_renting.rental_order_action').read()[0]
		action['domain'] = [('id', 'in', rental.ids)]
		action['views'] = [(self.env.ref('sale_renting.rental_order_view_tree').id, 'tree'),(self.env.ref('sale_renting.rental_order_primary_form_view').id, 'form')]

		return action



	#
	picking_count = fields.Integer(compute='_picking_count', string='Partners Count' )
	picking_ids = fields.One2many('stock.picking', 'partner_id') # Many2many

	def _picking_count(self):
		pickings = self.env['stock.picking'].search([('partner_id', '=', self.id)])
		self.picking_count = len(pickings)


	def action_create_picking(self):
		picking = self.mapped('picking_ids')
		action = self.env.ref('stock.action_picking_tree_all').read()[0]

		action['domain'] = [('id', 'in', picking.ids)]
		action['views'] = [(self.env.ref('stock.vpicktree').id, 'tree'),(self.env.ref('stock.view_picking_form').id, 'form')]

		return action

	fsm_task_count = fields.Integer(compute='_task_count', string='FSM task Count' )
	task_ids = fields.One2many('project.task', 'partner_id') # Many2many

	def _task_count(self):
		tasks = self.env['project.task'].search([('partner_id', '=', self.id)])
		self.fsm_task_count = len(tasks)


	def action_create_task(self):
		tasks = self.mapped('task_ids')
		action = self.env.ref('industry_fsm.project_task_action_fsm').read()[0]
		action['domain'] = [('id', 'in', tasks.ids)]
		action['views'] = [(self.env.ref('industry_fsm.project_task_view_list_fsm').id, 'tree'),(self.env.ref('industry_fsm.project_task_view_form').id, 'form'),(self.env.ref('industry_fsm.project_task_view_calendar_fsm').id, 'calendar'),(self.env.ref('project_enterprise.project_task_map_view').id, 'map'),(self.env.ref('project_enterprise.project_task_view_gantt').id, 'gantt')]
		return action