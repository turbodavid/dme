# -*- coding: utf-8 -*-
# Copyright 2018 Pc systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby
from openerp import api, fields, models
from openerp.exceptions import except_orm, Warning as UserError
from openerp.tools.translate import _
from operator import itemgetter
import logging

_logger = logging.getLogger(__name__)

class Create_invoice_taxes(models.TransientModel):
	_inherit = 'pos.make.invoice'

	@api.multi
	def make_invoice_taxes(self):
		"""Function that actual create the invoice from wizard data
		"""
		self.ensure_one()

		# Custom context for sent values to alter account move lines generated
		# by invoice
		account_receivable = self.partner_id.property_account_receivable.id
		new_account_unbilled_id = self.company_id.unbilled_account_id.id
		if not new_account_unbilled_id:
			raise UserError(
				_('You have to set up an account in Point of Sales '
					'into Invoice Settings')
			)
		ctx = {
	    	'order_account': account_receivable,
	    	'account_merchandise_unbilled': new_account_unbilled_id,
		}
		ctx.update(self._context)
		self = self.with_context(ctx)
		# Get data for invoice
		invoice_data = self._prepare_invoice(account_receivable)
		invoice = self.env['account.invoice'].create(invoice_data)
		all_lines = self.pos_orders.mapped('lines')
		# Group lines according to user selection
		invoice_lines = self._group_by_taxes(all_lines)
		invoice.write({'invoice_line': invoice_lines})
		#Update taxes on new invoice
		invoice.button_reset_taxes()
		invoice.invoice_open()
		# Reconcile invoice with payments
		pay_move_lines = self.pos_orders.mapped(
	    	'statement_ids.journal_entry_id.line_id',
		)
		pay_move_lines.write({'partner_id': self.partner_id.id})
		to_reconcile = pay_move_lines | invoice.move_id.line_id
		# Filter account move lines and left only the ones related with
		# current order partner, on receivable accounts and not already
		# reconciled
		to_reconcile = to_reconcile.filtered(
	    	lambda r: (
	        	r.account_id.type == 'receivable' and not r.reconcile_id
	    	)
		)
		try:
			to_reconcile.with_context(no_tax_reconile=True).reconcile()
		except except_orm:
		#TODO: logging error
			_logger.warning(
				'Something is wrong with the reconcile', exc_info=True
			)
		# Update pos orders with invoice data and state

		self.pos_orders.write({'invoice_id': invoice.id, 'state': 'invoiced'})
		#Return new view and open generated invoice
		return {
	    	'name': _('Customer Invoice'),
	    	'view_type': 'form',
	    	'view_mode': 'form',
	    	'res_model': 'account.invoice',
	    	'type': 'ir.actions.act_window',
	    	'target': 'current',
	    	'res_id': invoice.id or False,
		}

	def _group_by_taxes(self, lines=None):
		"""
		Helper function to group pos order lines by product
		@IDS of IVAS
		IVA 0% VENTAS ID = 23
		IVA 16% VENTAS ID = 8
		"""
		inv_line_ref = self.env['account.invoice.line']
		groups = {}
		for line in lines:
			key = (line.product_id.taxes_id)
			if key in groups:
				groups[key]['price_unit'] += line.price_subtotal
				groups[key]['invoice_line_tax_id'] = line.product_id.taxes_id
				print"Group", groups[key]['invoice_line_tax_id']
			else:
				groups[key] = {
					'price_unit': line.price_subtotal,
					'discount': line.discount,
					'qty': 1,
					'invoice_line_tax_id': line.product_id.taxes_id,
				}
		# Prepare invoice lines
		res = []
		for dummy, line in groups.iteritems():
			if line['invoice_line_tax_id'].id == 8:
				domain = [
					('default_code', '=', 'IVA16')
				]
				product = self.env['product.product'].search(domain, limit=1)
				values = {
					'product_id': product.id,
					'quantity': line['qty'],
					}
				values.update(
					inv_line_ref.product_id_change(
						product.id,
						product.uom_id.id,
						line['qty'],
						partner_id=self.partner_id.id,
						fposition_id=self.partner_id.property_account_position.id,
					)['value'],
				)
				if product.description_sale:
					values['note'] = product.description_sale
				values['price_unit'] = line['price_unit']
				values['discount'] = line['discount']
				values['name'] = product.name_template
				values['invoice_line_tax_id'] = [
					(6, 0, [x.id for x in product.taxes_id]),
				]
				res.append((0,0,values))
	        	#print"RESULTADO IVA16:", res
			elif line['invoice_line_tax_id'].id == 23:
	        	#print "Impuesto del 0% ventas
				domain = [
	        		('default_code', '=', 'IVA0')
				]
	        	product = self.env['product.product'].search(domain, limit=1)
	        	values = {
	        		'product_id': product.id,
	        		'quantity': line['qty'],
	        	}
	        	values.update(
	        		inv_line_ref.product_id_change(
	        			product.id,
	        			product.uom_id.id,
						line['qty'],
						partner_id=self.partner_id.id,
						fposition_id=self.partner_id.property_account_position.id,
					)['value'],
				)
	        	if product.description_sale:
	        		values['note'] = product.description_sale
            	values['price_unit'] = line['price_unit']
            	values['discount'] = line['discount']
            	values['name'] = product.name_template
            	values['invoice_line_tax_id'] = [
					(6, 0, [x.id for x in product.taxes_id]),
				]
            	res.append((0,0,values))
				#print"RESULTADO IVA0:", res
		#print"RESULTADO LINEA DE FACTURA: ",res
		return res