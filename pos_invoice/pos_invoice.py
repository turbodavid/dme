# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#    Coded By: Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from datetime import datetime, timedelta
import netsvc
import time
from openerp.tools.translate import _

#clase basada en l10n_mx_facturae/wizard
#http://acespritechblog.wordpress.com/2014/05/29/openerp-point-of-sale-create-invoice-for-multiple-orders-together/

class pos_invoice(osv.osv_memory):
	_name = 'pos.invoice'
	_description = "Create Invoice from POS"
	

	def init_search_pos(self, cr, uid, context = None):	
		#fecha actual
		date_order = time.strftime('%Y-%m-%d')
		#regresa los pos.order de la fecha actual
		return self.pool.get('pos.order').search(cr, uid, [
				('state', 'in', ['paid']),
				('date_order', '>=', date_order),
				('date_order', '<', date_order),
			], order='date_order')

	#Funcion que obtiene informacion con los filtros indicados
	def search_pos(self, cr, uid, ids, context = None):
		#crea una lista 
		pos_order_ids = []
		#obtiene los datos con el id activo
		data = self.read(cr, uid, ids, context=context)[0]
		if context is None:
			context = {}
		#obtiene un objeto de tipo pos.order
		pos_order_obj = self.pool.get('pos.order')
		#si trae ids de pos order
		if data['pos_order_ids']:
			pos_order_ids = []
		else:
			pos_order_ids = data['pos_order_ids']
		#asigna fecha inicial y final de pantalla
		date_start = data['date_start']
		date_end = data['date_end']
		#asigna los ids de pos order que cumplan con los filtros
		pos_order_ids.extend(
			pos_order_obj.search(cr, uid, [
				('state', 'in', ['paid']),
				('date_order', '>=', date_start),
				('date_order', '<', date_end),
			], order='date_order', context=context)
		)
		#asigna los ids de pos order encontrados a registro activo
		data['pos_order_ids'] = pos_order_ids
		#actualiza los ids de tabla many2many
		self.write(cr, uid, ids, {'pos_order_ids': [(6, 0, pos_order_ids)]}, context=None)
		#recarda de nuevo pantalla con los datos 
		ir_model_data = self.pool.get('ir.model.data')
		form_res = ir_model_data.get_object_reference(cr, uid, 'pos_invoice', 'pos_create_invoice_form_view')
		form_id = form_res and form_res[1] or False
		return {
			'type': 'ir.actions.act_window',
			'name': 'All pos order for invoice',
			'res_model': 'pos.invoice',
			'nodestroy': True,
			'target': 'new',
			'res_id': ids[0],
			'views': [(form_id, 'form')],
		}
	
	#Crea factura borrador
	def create_pos_invoice(self, cr, uid, ids, context = None):
		#Objetos de apoyo
		wf_service = netsvc.LocalService("workflow")
		pos_order_obj = self.pool.get('pos.order')
		inv_ref = self.pool.get('account.invoice')
		inv_line_ref = self.pool.get('account.invoice.line')
		product_obj = self.pool.get('product.product')
		res_partner_obj = self.pool.get('res.partner')
		inv_ids = []
		pos_lines = []
		#obtiene el objeto activo
		data = self.read(cr, uid, ids, context=context)[0]
		#No trae contexto inicializa
		if context is None:
			context = {}
		#revisa si tiene partner_id
		if not data['partner_id']:
			raise osv.except_osv(_('Error!'), _('Please provide a partner for the invoice.'))
		#revisa si tiene pos order
		if not data['pos_order_ids']:
			raise osv.except_osv(_('Error!'), _('Please provide a pos order.'))
		#revisa si tiene date_invoice
		if not data['date_invoice']:
			raise osv.except_osv(_('Error!'), _('Please provide a date invoice.'))
		#Pendiente 
		# Revisar que sean del mismo sale_journal, pricelist

		#Obtiene al partner
		res_partner = res_partner_obj.browse(cr, uid, data['partner_id'][0], context=context)
		#variable para almacenar la referencia del pos.order
		pos_order_ref = ''
		sale_journal_id = None
		currency_id = None

		#recorre los ids de pos order		
		for order in self.pool.get('pos.order').browse(cr, uid, data['pos_order_ids'], context=context):
			#empieza a revisar el sale journal
			if sale_journal_id == None:
				sale_journal_id = order.sale_journal.id
			else:
				if sale_journal_id != order.sale_journal.id:
					raise osv.except_osv(_('Error!'), _('Sales Journal of POS Order are different.'))
			#empieza a revisar el currency id
			if currency_id == None:
				currency_id = order.pricelist_id.currency_id.id
			else:
				if currency_id != order.pricelist_id.currency_id.id:
					raise osv.except_osv(_('Error!'), _('currency of POS Order are different.'))			
			#Concatena referencia del pos.order
			pos_order_ref += order.name + '|'
			#Recorre las lineas de pos order y agrega a lista
			for line in order.lines:
				pos_lines.append(line)

		#Agrupa por Id producto y precio
		pos_lines_sort = []		
		enc = 0
		for line in pos_lines:
			for sort in pos_lines_sort:
				if (line.product_id.id == sort.product_id.id and line.price_unit == sort.price_unit):
					enc = 1
					sort.qty = sort.qty + line.qty
					break
				else:
					enc = 0
			if enc == 0:
				pos_lines_sort.append(line)
				
		#for pos in pos_lines_sort:
		#	print pos.product_id.id
		#	print pos.qty
		#return False

		#Quita el ultimo '|' en pos_order_ref
		if len(pos_order_ref) >= 1: 
			pos_order_ref = pos_order_ref[:-1]

		#Factura Encabezado
		inv = {
                'name': pos_order_ref,
                'origin': pos_order_ref,
                'account_id': res_partner.property_account_receivable.id,
                'journal_id': sale_journal_id,
                'type': 'out_invoice',
                'reference': pos_order_ref,
                'partner_id': res_partner.id,
                #'comment': order.note or '',
                'currency_id': currency_id,
				'date_invoice': data['date_invoice'],
            }
		#Actualiza factura
		inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', res_partner.id)['value'])
		#No Obtuvo la cuenta 
		if not inv.get('account_id', None):
			inv['account_id'] = res_partner.property_account_receivable.id
		#Crea la Factura Encabezado
		inv_id = inv_ref.create(cr, uid, inv, context=context)
		#Actualiza el partner
		pos_order_obj.write(cr, uid, data['pos_order_ids'], {'partner_id': res_partner.id}, context=context)
		#Actualiza los pos order con el id de la factura creada
		pos_order_obj.write(cr, uid, data['pos_order_ids'], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
		#Agrega el id de la factura		
		inv_ids.append(inv_id)
		#Detalles Factura
		for line in pos_lines_sort:#pos_lines:
			inv_line = {
				'invoice_id': inv_id,
				'product_id': line.product_id.id,
				'quantity': line.qty,
			}
			inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
			inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
															line.product_id.id,
															line.product_id.uom_id.id,
															line.qty, partner_id = res_partner.id,
															fposition_id = res_partner.property_account_position.id)['value'])
			if line.product_id.description_sale:
				inv_line['note'] = line.product_id.description_sale
			inv_line['price_unit'] = line.price_unit
			inv_line['discount'] = line.discount
			inv_line['name'] = inv_name
			inv_line['invoice_line_tax_id'] = [(6, 0, [x.id for x in line.product_id.taxes_id] )]
			inv_line_ref.create(cr, uid, inv_line, context=context)
		#Actualiza impuestos
		inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
		#trigger solo cambia el state para mantener el workflow
		for pos in data['pos_order_ids']:
			wf_service.trg_validate(uid, 'pos.order', pos, 'invoice', cr)
		#No almaceno el id de la factura
		if not inv_ids: return {}

		#Manda a Forma de Factura
		mod_obj = self.pool.get('ir.model.data')
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
		res_id = res and res[1] or False
		return {
			'name': _('Customer Invoice'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': inv_ids and inv_ids[0] or False,
		}

	_columns = {
		'date_invoice': fields.date('Date Invoice'),
		'date_start': fields.date('Date Start', required=True),
		'date_end': fields.date('Date End', required=True),
		'partner_id' : fields.many2one('res.partner', string="Partner", 
            domain=[('customer','=',True)]
            ),
        'pos_order_ids': fields.many2many('pos.order',
            'pos_invoice_wizard', 'pos_invoice_id', 'pos_order_id',"Pos Order's",
            domain="[('state', 'in', ['paid'] )]",
            help="Pos Order's that meet with the filter"),
	}
	_defaults = {
		'date_start': lambda *a: time.strftime('%Y-%m-%d'),
		'date_end': lambda *a: time.strftime('%Y-%m-%d'),
		'pos_order_ids': init_search_pos,
		'date_invoice': lambda *a: time.strftime('%Y-%m-%d'),	
	}

#Clase para relacionar el pos_invoice con pos_order
class pos_invoice_Wizard(osv.Model):
	_name = 'pos.invoice.wizard'
	_auto = False # No genera los campos automaticos
	_columns = {
		'pos_invoice_id':fields.many2one('pos.invoice'),
		'pos_order_id': fields.many2one('pos.order'),
	}
