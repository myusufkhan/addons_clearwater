# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import calendar
from odoo.exceptions import UserError

class SaleOrderExtended(models.Model):
	_inherit = 'sale.order'
	contract_terms = fields.Selection([('monthly', 'Months'),('weekly', 'weeks'),],string='Contract', default=False,help="""This will create multiple order lines depending on state""")
	deliveries_count = fields.Integer(help="Number of Division of sale order line.")


	def create_contract_terms(self):
		date = datetime.date.today()
		order_line = self.order_line
		if not order_line:
			if not self.order_line:
				raise UserError(_("Add product First"))
		if len(order_line) == 1:
			if self.contract_terms == False and self.contract_terms == False:
				raise UserError(_("Select Contract Term First"))
			if self.deliveries_count > 1 and self.contract_terms:
				order_line.from_contract_term = True
				if self.contract_terms == 'monthly':
					for x in range(self.deliveries_count - 1):
						date = self.add_months(date, 1)
						order_line.dup_line(self.id,date)

				elif self.contract_terms == 'weekly':
					for x in range(self.deliveries_count-1):
						date = self.add_week(date, 1)
						order_line.dup_line(self.id, date)
		else:
			raise UserError(_("Changes allowed only when there is one line in Sale Order Line"))

	def add_months(self,sourcedate, months):
		month = sourcedate.month - 1 + months
		year = sourcedate.year + month // 12
		month = month % 12 + 1
		day = min(sourcedate.day, calendar.monthrange(year, month)[1])
		return datetime.date(year, month, day)
	def add_week(self,sourcedate, weeks):
		date = sourcedate + datetime.timedelta(weeks = weeks)
		return date

class SaleOrderLineExtended(models.Model):
	_inherit = 'sale.order.line'
	order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True,
	                           copy=True)
	from_contract_term = fields.Boolean(default = False, help="if checked the delivery will be splitted and if not same product will be merged in delivery (this tick enables working of Contract Terms)")

	def dup_line(self,order_id,date):
		self.copy(default={'order_id': order_id,'delivery_date_custom': date,'from_contract_term' :True})

	delivery_date_custom = fields.Datetime('Delivery Date',
        help="Choose a date to get the delivery at that date",
        default=fields.Datetime.now)

	def _prepare_procurement_values(self, group_id=False,is_split=False):
		""" Prepare specific key for moves or other components that will be created from a stock rule
		comming from a sale order line. This method could be override in order to add other custom key that could
		be used in move/po creation.
		"""
		values = super(SaleOrderLineExtended, self)._prepare_procurement_values(group_id)
		self.ensure_one()
		date_planned = self.order_id.date_order \
		               + timedelta(days=self.customer_lead or 0.0) - timedelta(
			days=self.order_id.company_id.security_lead)
		values.update({
			'group_id': group_id,
			'sale_line_id': self.id,
			'date_planned': date_planned,
			'route_ids': self.route_id,
			'warehouse_id': self.order_id.warehouse_id or False,
			'partner_id': self.order_id.partner_shipping_id.id,
			'company_id': self.order_id.company_id,
		})
		if is_split == True:
			for line in self:
				date_planned = fields.Datetime.from_string(line.delivery_date_custom) - timedelta(
					days=line.order_id.company_id.security_lead)
				values.update({
					'date_planned': fields.Datetime.to_string(date_planned),
				})
		else:
			for line in self.filtered("order_id.commitment_date"):
				date_planned = fields.Datetime.from_string(line.order_id.commitment_date) - timedelta(
					days=line.order_id.company_id.security_lead)
				values.update({
					'date_planned': fields.Datetime.to_string(date_planned),
				})

		return values


	def _action_launch_stock_rule(self, previous_product_uom_qty=False):
		"""
		Launch procurement group run method with required/custom fields genrated by a
		sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
		depending on the sale order line product rule.
		"""
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		procurements = []
		for line in self:
			if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
				continue
			qty = line._get_qty_procurement(previous_product_uom_qty)
			if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
				continue

			group_id = line._get_procurement_group()
			updated_vals = {}
			if line.from_contract_term:
				group_id1 = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
				# line.order_id.procurement_group_id = group_id
				values = line._prepare_procurement_values(group_id=group_id1,is_split=True)
			else:
				if not group_id:
					group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
					line.order_id.procurement_group_id = group_id
				else:
					if group_id.partner_id != line.order_id.partner_shipping_id:
						updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
					if group_id.move_type != line.order_id.picking_policy:
						updated_vals.update({'move_type': line.order_id.picking_policy})
					if updated_vals:
						group_id.write(updated_vals)
			if not line.from_contract_term:
				values = line._prepare_procurement_values(group_id=group_id)
			product_qty = line.product_uom_qty - qty

			line_uom = line.product_uom
			quant_uom = line.product_id.uom_id
			product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
			procurements.append(self.env['procurement.group'].Procurement(
				line.product_id, product_qty, procurement_uom,
				line.order_id.partner_shipping_id.property_stock_customer,
				line.name, line.order_id.name, line.order_id.company_id, values))


		if procurements:
			self.env['procurement.group'].run(procurements)
		return True

# _get_stock_move_values

	# @api.depends('product_id', 'customer_lead', 'product_uom_qty', 'order_id.warehouse_id', 'order_id.commitment_date')
	# def _compute_qty_at_date(self):
	# 	""" Compute the quantity forecasted of product at delivery date. There are
	# 	two cases:
	# 	 1. The quotation has a commitment_date, we take it as delivery date
	# 	 2. The quotation hasn't commitment_date, we compute the estimated delivery
	# 		date based on lead time"""
	# 	qty_processed_per_product = defaultdict(lambda: 0)
	# 	grouped_lines = defaultdict(lambda: self.env['sale.order.line'])
	# 	# We first loop over the SO lines to group them by warehouse and schedule
	# 	# date in order to batch the read of the quantities computed field.
	# 	for line in self:
	# 		if not line.display_qty_widget:
	# 			continue
	# 		line.warehouse_id = line.order_id.warehouse_id
	# 		if line.order_id.commitment_date:
	# 			date = line.order_id.commitment_date
	# 		else:
	# 			confirm_date = line.order_id.date_order if line.order_id.state in ['sale', 'done'] else datetime.now()
	# 			date = confirm_date + timedelta(days=line.customer_lead or 0.0)
	# 		grouped_lines[(line.warehouse_id.id, date)] |= line
	#
	# 	treated = self.browse()
	# 	for (warehouse, scheduled_date), lines in grouped_lines.items():
	# 		product_qties = lines.mapped('product_id').with_context(to_date=scheduled_date, warehouse=warehouse).read([
	# 			'qty_available',
	# 			'free_qty',
	# 			'virtual_available',
	# 		])
	# 		qties_per_product = {
	# 			product['id']: (product['qty_available'], product['free_qty'], product['virtual_available'])
	# 			for product in product_qties
	# 		}
	# 		for line in lines:
	# 			line.scheduled_date = scheduled_date
	# 			qty_available_today, free_qty_today, virtual_available_at_date = qties_per_product[line.product_id.id]
	# 			line.qty_available_today = qty_available_today - qty_processed_per_product[line.product_id.id]
	# 			line.free_qty_today = free_qty_today - qty_processed_per_product[line.product_id.id]
	# 			line.virtual_available_at_date = virtual_available_at_date - qty_processed_per_product[
	# 				line.product_id.id]
	# 			qty_processed_per_product[line.product_id.id] += line.product_uom_qty
	# 		treated |= lines
	# 	remaining = (self - treated)
	# 	remaining.virtual_available_at_date = False
	# 	remaining.scheduled_date = False
	# 	remaining.free_qty_today = False
	# 	remaining.qty_available_today = False
	# 	remaining.warehouse_id = False

