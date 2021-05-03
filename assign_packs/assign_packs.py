# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#    Coded By: Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
#			Jesús Antonio Meza Espinoza (jesus.meza@dmesoluciones.com)
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

class assign_packs(osv.Model):
	_name = 'assign.packs'
	_description = "Assign Packs"

	def _validate_tracking(self, cr, uid, ids, values):
		tracking_ids_query = ''
		#Obtiene los paquetes
		for tracking_id in values["tracking_ids"]:
			for i in tracking_id[2]:
				tracking_ids_query = tracking_ids_query + str(i) + ","

		#quita el ultima coma
		if tracking_ids_query !='':
			tracking_ids_query = tracking_ids_query[:-1]
		print tracking_ids_query

		#Query para revisar relación
		sql_req= """SELECT r.tracking_id, a.name as partner, s.name as shop, t.name as tracking
			From assign_packs_rel r
			Inner Join assign_packs p on r.assign_packs_id = p.id
			Left Join res_partner a on partner_id = a.id
			Inner Join sale_shop s on p.shop_id = s.id
			Inner Join stock_tracking t on r.tracking_id = t.id
			Where (tracking_id in (%s)) and (r.assign_packs_id <> %d)  Order by t.name""" % (tracking_ids_query,ids[0])
		cr.execute(sql_req)
		sql_res = cr.dictfetchall()
		if sql_res:
			message = _('A record with the same pack already exists \n')
			for result in sql_res:
				message = message + _("Pack: ") + result["tracking"] + _(" Assign: ") + result["shop"] + "\n"
			raise osv.except_osv(_('Error!'), message)
		return True

	def write(self, cr, uid, ids, values, context=None):
		# Se verifica que se hayan cambiado los paquetes
		if ('tracking_ids' in values.values()):
			# Valida los paquetes
			result = self._validate_tracking(cr, uid, ids, values)
		else:
			result = True

		#Todo es correcto
		if (result):
			res = super(assign_packs,self).write(cr,uid,ids,values,context=context)
			return res

	def create(self, cr, uid, values, context=None):
		#Valida los paquetes
		result = self._validate_tracking(cr, uid, [0], values)
		#Todo es correcto
		if (result):
			# Se obtiene el nombre o folio de la asignacion de los paquetes
			if values.get('name', '/')=='/':
				values['name'] = self.pool.get('ir.sequence').get(cr, uid, 'assign.packs') or '/'

			#Guarda normal
			res = super(assign_packs,self).create(cr,uid,values,context=context)
			return res

	def unlink(self, cr, uid, ids, context=None):
		result = False
		for assign_id in ids:
			# Se obtiene la Asignacion
			assign_pack = self.pool.get('assign.packs').browse(cr, uid, assign_id, context=context)
			
			# Se verifica que se pueda borrar
			if(assign_pack.state != 'done'):
				result = super(assign_packs, self).unlink(cr, uid, assign_id, context=context)
			else:
				if(len(ids) > 1):
					raise osv.except_osv(_(u'Error'), _(u"Can\'t delete because some the Assign Pack it\'s Done."))
				else:
					raise osv.except_osv(_(u'Error'), _(u"Can\'t delete when the Assign Pack it\'s Done."))
		return result

	def _get_default_shop(self, cr, uid, context=None):
		company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
		shop_ids = self.pool.get('sale.shop').search(cr, uid, [('company_id','=',company_id)], context=context)
		if not shop_ids:
			raise osv.except_osv(_('Error!'), _('There is no default shop for the current user\'s company!'))
		return shop_ids[0]

	def action_button_confirm(self, cr, uid, id, values, context=None):
		# Se obtiene la Asignacion del Paquete
		assign_pack = self.pool.get('assign.packs').browse(cr, uid, id, context=None)
		
		# Se verifica que tenga un Colaborador
		if(assign_pack[0].partner_id.id == False):
			raise osv.except_osv(_(u'Error!'), _(u"The Assign Pack needs a Partner."))
		
		# Se modifica el estatus a "Abierto" para imprimir
		result = super(assign_packs, self).write(cr, uid, id, {'state': 'open'}, context=context)
		return result

	def action_button_process(self, cr, uid, assign_id, context=None):
		# Se obtiene la Asignacion del Paquete
		assign_pack = self.pool.get('assign.packs').browse(cr, uid, assign_id, context=None)
		
		# Se verifica que tenga un Colaborador
		if(assign_pack[0].partner_id.id == False):
			raise osv.except_osv(_(u'Error!'), _(u"The Assign Pack needs a Partner."))
		
		# Se obtiene el Producto
		product = self.pool.get('product.product').browse(cr, uid, assign_pack[0].product_id.id, context=None)
		
		# Se obtiene el usuario para obtener id company
		user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
		
		# Variable de trabajo para el Do Partial
		move_values = {}
		
		# Se obtienen el total de los Paquetes
		total_packs = len(assign_pack[0].tracking_ids)
		# Se obtiene el descuento para cada producto con base en la comision que se le asigno
		discount = product.lst_price * (assign_pack[0].commission_percent / 100)
		total = product.lst_price * total_packs

		# Se llenan los datos del Encabezado de la Cotizacion
		sale_order_id = self.pool.get('sale.order').create(cr, uid, {
																	'shop_id': assign_pack[0].shop_id.id,
																	'partner_id': assign_pack[0].partner_id.id,
																	'user_id': uid,
																	'company_id': assign_pack[0].shop_id.company_id.id,
																	'amount_tax': 0.00,
																	'state': 'draft',
																	'pricelist_id': 1,
																	'partner_invoice_id': assign_pack[0].partner_id.id,
																	'amount_untaxed': 0.00,
																	'amount_total': 0.00,
																	'partner_shipping_id': assign_pack[0].partner_id.id,
																	'invoice_quantity': 'order',
																	'picking_policy': 'direct',
																	'shipped': False,
																	'currency_id': 34, # Peso Mexicano
																	'date_confirm': False,
																	'client_order_ref': '',
																	'invoice_ids': [],
																	'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.order'),
																	}, context=context)		
		
		# Se crea el detalle
		self.pool.get('sale.order.line').create(cr, uid, {
															'product_uos_qty': total_packs * 10, # Por cada Block son diez boletos
															'product_uom': product.product_tmpl_id.uom_id.id,
															'sequence': 10,
															'order_id': sale_order_id,
															'price_unit': product.lst_price, # Se multiplica por diez porque c/paquete tiene diez boletos
															'product_uom_qty': total_packs * 10,
															'discount': assign_pack[0].commission_percent,
															'name': product.name, #'Sort',
															'company_id': user.company_id.id,
															'salesman_id': uid,
															'state': 'draft',
															'product_id': product.id,
															'order_partner_id': assign_pack[0].partner_id.id,
															'invoiced': False,
															'type': 'make_to_order',
															'delay': 7,
														}, context=context)
	
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Se confirma la Cotizacion
		wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'order_confirm', cr)
		# Se crea la Factura del Pedido de Venta (antes Cotizacion)
		wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'manual_invoice', cr)
		
		# Se obtiene la Venta
		sale_order = self.pool.get('sale.order').browse(cr, uid, sale_order_id, context=None)
		# Se obtiene la Factura creada
		account_invoice_id = self.pool.get('account.invoice').search(cr, uid, [('origin', '=', sale_order.name)])
		account_invoice = self.pool.get('account.invoice').browse(cr, uid, account_invoice_id, context=None)
		
		# Se Valida la Factura
		wf_service.trg_validate(uid, 'account.invoice', account_invoice[0].id,'manual_invoice', cr)
		# Se Confirma la Factura
		wf_service.trg_validate(uid, 'account.invoice',account_invoice[0].id,'invoice_open', cr)

		stock_picking_out = self.pool.get('stock.picking.out')
		stock_picking_out_id = stock_picking_out.search(cr, uid, [('state','=','confirmed'), ('type','=','out'), ('origin', '=', sale_order.name)])
		
		# Se obtiene la Salida de Albaran
		pick = stock_picking_out.browse(cr, uid, stock_picking_out_id)
		
		for move in pick[0].move_lines:
			# Se insertan los nuevos detalles
			#for i in range(int(move.product_qty)):
			first_row = True
			for tracking in assign_pack[0].tracking_ids:
				# Por cada tracking se obtiene el limite mayor de boletos
				str_up_limit = tracking.name + '0'
				int_up_limit = int(str_up_limit)
				print int_up_limit
				r = 10
				while r > 0:
					# Verifica que sea el primer registro y disminuye dos en caso de serlo
					if (first_row):
						# Se disminuye en uno el limite superior
						# JORGE int_up_limit -= 1
						# Se disminuye en uno la variable de control del bucle
						# JORGE  r -= 1
						# Se busca el Prod Lot
						prod_lot_id = self.pool.get('stock.production.lot').search(cr, uid, [('name', '=', str_up_limit)])
						
						# Se verifica que se haya encontrado el numero de serie
						if(prod_lot_id):
							# Se obtiene el numero de serie
							prod_lot = self.pool.get('stock.production.lot').browse(cr, uid, prod_lot_id, context=None)
							# Se actualiza el movimiento principal
							self.pool.get('stock.move').write(cr, uid, move.id, {
																					'product_uos_qty': 1.0,
																					'product_qty': 1.0,
																					'tracking_id': tracking.id,
																					'prodlot_id': prod_lot[0].id,
																				})
							move_values['move%s'%(move.id)] = {
																'prodlot_id':False,
																'product_id': move.product_id.id,
																'product_qty': 1.0,
																'product_uom': move.product_uom.id,
																'product_price': move.price_unit,
																'delivery_date': time.strftime('%Y-%m-%d'),
															}
							#~ move_values['delivery_date'] = time.strftime('%Y-%m-%d')
							# Se disminuye en uno el limite superior
							int_up_limit -= 1
							# Se disminuye en uno la variable de control del bucle
							r -= 1
						else:
							raise osv.except_osv(_(u'Error'), _(u"The Serial Number is not found " + str_up_limit + "."))
						
						first_row = False
					#else: # Else JORGE
						# Se disminuye en uno el limite superior
					#	int_up_limit -= 1
						# Se disminuye en uno la variable de control del bucle
					#	r -= 1
					
					# Se busca el Prod Lot
					prod_lot_id = self.pool.get('stock.production.lot').search(cr, uid, [('name', '=', str(int_up_limit))])
					
					# Se verifica que se haya encontrado el numero de serie
					if(prod_lot_id):
						# Se obtiene el numero de serie
						prod_lot = self.pool.get('stock.production.lot').browse(cr, uid, prod_lot_id, context=None)
						# Se guarda el detalle
						move_id = self.pool.get('stock.move').create(cr, uid, {
																					'origin': sale_order.name,
																					'product_uos_qty': 1.0,
																					'product_uom': move.product_uom.id,
																					'price_unit': move.price_unit,
																					'product_qty': 1.0,
																					'product_uos': move.product_uos.id,
																					'partner_id': assign_pack[0].partner_id.id,
																					'name': product.name,
																					'product_id': product.id,
																					'auto_validate': False,
																					'location_id': move.location_id.id,
																					'company_id': user.company_id.id,
																					'picking_id': pick[0].id,
																					'state': 'confirmed',
																					'location_dest_id': move.location_dest_id.id,
																					'sale_line_id': move.sale_line_id.id,
																					'tracking_id': tracking.id,
																					'prodlot_id': prod_lot[0].id,
																				}, context=context)
						#Se disminuye en uno el limite superior
						int_up_limit -= 1
						# Se disminuye en uno la variable de control del bucle
						r -= 1
						move_values['move%s'%(move_id)] = {
											'prodlot_id':False,
											'product_id': move.product_id.id,
											'product_qty': 1.0,
											'product_uom': move.product_uom.id,
											'product_price': move.price_unit,
											'delivery_date': time.strftime('%Y-%m-%d'),
											}
						#~ move_values['delivery_date'] = time.strftime('%Y-%m-%d')
					else:
						raise osv.except_osv(_(u'Error'), _(u"The Serial Number is not found " + str(int_up_limit) + "."))

				#~ print 'Antes del do partial'
				#~ print move_values
				# Se le cambia la fecha para el Do Partial
				#~ move_values['delivery_date'] = time.strftime('%Y-%m-%d')
				#~ print time.strftime('%Y-%m-%d')
				#~ print move_values['delivery_date']
		#~ print 'Intenta hacer el do partial'
		print move_values
		# Do Partial
		#~ for picking_id in stock_picking_out_id:
			#~ stock_picking_out.do_partial(cr, uid, picking_id, move_values)
		stock_picking_out.do_partial(cr, uid, [pick[0].id], move_values)
		#~ print 'Hizo el do partial'
		
		# Se limpia partial_datas
		#~ move_values.clear()
		
		#~ wf_service.trg_validate(uid, 'stock.picking', stock_picking_out_id,'button_done', cr)
		#~ wf_service.trg_validate(uid, 'stock.picking', stock_picking_out_id,'force_assign', cr)
		#~ wf_service.trg_validate(uid, 'stock.picking', stock_picking_out_id,'action_process', cr)
		
		# Se atualiza el Estatus de la Asignacion de Paquete
		result = super(assign_packs, self).write(cr, uid, assign_id, {'state': 'done'}, context=context)
		return result

	def action_button_print(self, cr, uid, ids, context=None):
		# Se manda llamar al servicio para imprimir este reporte
		datas = {
					 'model': 'assign.packs',
					 'ids': ids,
					 'form': self.read(cr, uid, ids[0], context=context),
			}
		return {'type': 'ir.actions.report.xml', 'report_name': 'assign.packs', 'datas': datas, 'nodestroy': True}

##    def get_commission_percent(self, n):
##        # Se establece un valor default
##        percent = 0.00
##
##        # Se valida el porcentaje de comision
##        if n<5:
##            percent = 0
##        elif n>=5 and n<=29:
##            percent = 10
##        elif n>=30 and n<=59:
##            percent = 15
##        elif n>=60 and n<=149:
##            percent = 20
##        elif n>=150 and n<=229:
##            percent = 25
##        elif n>=230 and n<=699:
##            percent = 30
##        elif n>=700 and n<=999:
##            percent = 32.5
##        elif n>=1000 and n<=2499:
##            percent = 35
##        else:
##            percent = 38
##
##        # Se devuelve el porcentaje
##        return percent

	_columns = {
		'name': fields.char('Assign Pack Reference', size=64, required=True,
			readonly=True, states={'draft': [('readonly', True)], 'open': [('readonly', True)], 'done': [('readonly', True)]},
			select=True),
		'state': fields.selection([
			('draft', 'Draft'),
			('open', 'Open'),
			('done', 'Done')],string="State"),
		'date_assign': fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'done': [('readonly', True)]}),
		'partner_id' : fields.many2one('res.partner', string="Campaign Worker", domain=[('customer','=',True), ('parent_id','=',None)], states={'done': [('readonly', True)]}),
		'shop_id': fields.many2one('sale.shop', 'Shop', required=True, states={'done': [('readonly', True)]}),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)],required=True, states={'done': [('readonly', True)]}),
		'commission_percent': fields.float('Commission Percent', required=True, readonly=False, states={'done': [('readonly', True)]}), #fields.function(_get_commission_percent, obj='assign.packs',store=True, method=True, string= 'Commission Percent'),
		'tracking_ids': fields.many2many('stock.tracking',
			'assign_packs_rel', 'assign_packs_id', 'tracking_id',"Packs",
			help="Packs", states={'done': [('readonly', True)]}),
	}

	_defaults = {
		'name': lambda obj, cr, uid, context: '/',
		'shop_id': _get_default_shop,
		'state': 'draft',
		'commission_percent': 0,
	}

	_sql_constraints = [
		('name_uniq', 'unique(name)', 'Assign Pack Reference must be unique!'),
	]

#Clase para relacionar
class assign_packs_rel(osv.Model):	
	_name = "assign.packs.rel"
	_auto = False # No genera los campos automaticos
	_columns = {
		'assign_packs_id':fields.many2one('assign.packs'),
		'tracking_id': fields.many2one('stock.tracking'),
	}

	_sql_constraints = [
		('assign_packs_rel_unique', 'unique(tracking_id)', _('A record with the same pack already exists.')),
	]
