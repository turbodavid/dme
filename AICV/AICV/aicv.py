# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#    Jorge Medina jorge.medina@dmesoluciones.com
#    Jesús Meza jesus.meza@dmesolouciones.com
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

class aicv(osv.Model):
	_name = "aicv"
	
	#Funcion para Procesar todas las Compras completamente
	def action_aicv(self, cr, uid, ids, context=None):
		# Crea objeto de compra
		purchase_obj = self.pool.get('purchase.order')
		
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('id', '=', uid)])
		print user_ids
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		for user_id in user_ids:
			# Se obtiene
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Se ejecuta el proceso de Compras con el usuario: %s'%res_user.login
			
			# Obtiene las Compras borrador de la empresa del usuario actual
			order_ids = purchase_obj.search(cr, user_id, [('state','=','draft'), ('company_id', '=', res_user.company_id.id)])
			# Crea WorkFlow
			wf_service = netsvc.LocalService("workflow")
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(order_ids)
			noRegistroActual = 1
			
			#recorre las compras
			order_id = 0
			for order_id in order_ids:
				Mensaje = res_user.login + ' ==> ' + 'Confirmando Compra ' + noRegistroActual + ' de ' + totalRegistros
				print Mensaje
				#print 'Confirmando compra:%s'%order_id
				# Confirma la Compra
				wf_service.trg_validate(user_id, 'purchase.order',order_id,'purchase_confirm', cr)
			
				# Valida la Compra
				wf_service.trg_validate(user_id, 'purchase.order',order_id,'purchase_approve', cr)
			
			# Crea objeto stock picking in
			stock_picking_in_obj = self.pool.get('stock.picking.in')
			
			# Crea objeto stock move
			stock_move_obj = self.pool.get('stock.move')
			
			#~ # Busca las Entradas Asignadas de la empresa del usuario actual
			stock_picking_in_ids = stock_picking_in_obj.search(cr,user_id,[('state','=','assigned'), ('type','=','in'), ('company_id', '=', res_user.company_id.id)])
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(stock_picking_in_ids)
			noRegistroActual = 1
			
			# Recorre los Stock pendientes de recibir
			for stock_picking_in_id in stock_picking_in_ids:
				Mensaje = res_user.login + ' ==> ' + 'Procesando Stock In ' + noRegistroActual + ' de ' + totalRegistros
				print Mensaje
				#print 'Stock picking:%s'%stock_picking_in_id
				pick = stock_picking_in_obj.browse(cr, user_id, stock_picking_in_id)
				
				partial_datas={}
				
				# Recorre los Movimientos de cada picking
				for move in pick.move_lines:
					partial_datas['move%s'%(move.id)]= {
						'prodlot_id':False,
						'product_id': move.product_id.id,
						'product_qty': move.product_qty,
						'product_uom': move.product_uom.id,
						'product_price': move.price_unit,
						#'product_currency': move.price_currency_id,
					}
				partial_datas['delivery_date']= time.strftime('%Y-%m-%d')
				
				# do Partial
				stock_picking_in_obj.do_partial(cr, user_id, [stock_picking_in_id], partial_datas)
				
				# Se limpia partial_datas
				partial_datas.clear()
			
			# Se crea el objeto de Factura
			account_invoice = self.pool.get('account.invoice') # Objeto Principal
			account_invoice_obj = self.pool.get('account.invoice') # Objeto Auxiliar
			
			# Obtiene las Facturas borrador de la empresa del usuario actual
			invoice_ids = account_invoice.search(cr, user_id, [('state','=','draft'), ('type', '=', 'in_invoice'),('company_id', '=', res_user.company_id.id)])
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(invoice_ids)
			noRegistroActual = 1
			
			# Recorre las Facturas
			invoice_id = 0
			for invoice_id in invoice_ids:
				Mensaje = res_user.login + ' ==> ' + 'Procesando Factura ' + noRegistroActual + ' de ' + totalRegistros
				print Mensaje
				#print 'Factura:%s'%invoice_id
				# Se obtiene la Factura antes de confirmar
				account_invoice_obj = account_invoice.browse(cr, user_id, invoice_id)
				
				# Se obtiene la Compra utilizando el Folio de Referencia de la Factura
				order_id = purchase_obj.search(cr, user_id, [('state','=','approved'), ('company_id', '=', res_user.company_id.id), ('name', '=', account_invoice_obj.origin)])
				purchase_order = purchase_obj.browse(cr, user_id, order_id)
				
				# Para factura es date_invoice
				account_invoice_obj.date_invoice = purchase_order[0].date_order
				
				# Se actualiza el campo de la Fecha de la Factura
				account_invoice.write(cr, user_id, account_invoice_obj.id, {'date_invoice':account_invoice_obj.date_invoice, 'supplier_invoice_number':purchase_order[0].name}, context=context)
				
				# Confirma la Factura
				wf_service.trg_validate(user_id, 'account.invoice',invoice_id,'invoice_open', cr)
	# Funcion para Field Function
	def action_ventas(self, cr, uid, ids, context = None):
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('id', '=', uid)])
		#print user_ids
		
		res_user = res_user_obj.browse(cr, uid, user_id)
		print 'Se ejecuta el proceso de Ventas con el usuario: %s'%res_user.login
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		for user_id in user_ids:
			# Se obtiene el usuario administrador
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Usuario Id: %s'%user_id
			
			# Se crea el obtjeto de Ventas
			sale_order = self.pool.get('sale.order')
			# Se obtienen todas las ventas
			sale_ids = sale_order.search(cr, user_id, [('state', '=', 'draft')])
			
			print "============ Confirmar Ventas ================="
			print 'Ventas: %s'%(sale_ids)
			
			#4 CONFIRMAR VENTAS
			for sale_id in sale_ids:    
				print "Confirmando Venta Id: %s"%(sale_id)
				#workflow('sale.order', 'order_confirm', so)
				wf_service.trg_validate(user_id, 'sale.order', sale_id,'order_confirm', cr)
			
			#5 BUSQUEDA VENTAS A FACTURAS
			print "============ Crear Facturas Borrador ================="
			#~ so_ids = execute('sale.order', 'search', [('state','=','manual')])
			# Se crea el obtjeto de Factura
			account_invoice = self.pool.get('account.invoice')
			# Se obtienen todas las ventas
			sale_ids = sale_order.search(cr, user_id, [('state', '=', 'manual')])
			
			#6 CREAR FACTURA
			for sale_id in sale_ids:    
				print "Id Venta # %s"%(sale_id)
				# confirm  SOs
				#workflow('sale.order', 'manual_invoice', so)
				wf_service.trg_validate(user_id, 'sale.order', sale_id,'manual_invoice', cr)
			
			#7 BUSQUEDA DE FACTURAS DE VENTA BORRADOR
			print "============ Validar Factura Venta ================="
			
			# Crea objeto de Factura
			account_invoice = self.pool.get('account.invoice')
			#invoice_ids = execute('account.invoice', 'search', [('state','=','draft'), ('type','=','out_invoice')])
			invoice_ids = account_invoice.search(cr, user_id, [('state', '=', 'draft'), ('type','=','out_invoice')])
			
			#8 VALIDA FACTURAS
			for invoice_id in invoice_ids:
				print "Validar Factura Id: %s"%(invoice_id)
				# confirm  AIs
				#workflow('account.invoice', 'invoice_open', ai)
				wf_service.trg_validate(user_id, 'account.invoice', invoice_id,'manual_invoice', cr)
				
				# Se obtiene la Factura antes de confirmar
				account_invoice_obj = account_invoice.browse(cr, user_id, invoice_id)
				#print 'Origen de la Factura:'
				#print account_invoice_obj.origin
				#print ''
				
				# Se obtiene la Venta utilizando el Folio de origen de la venta
				sale_id = sale_order.search(cr, user_id, [('state','=','progress'), ('company_id', '=', res_user.company_id.id), ('name', '=', account_invoice_obj.origin)])
				sale_order_obj = sale_order.browse(cr, user_id, sale_id)
				#print 'Venta Id %s'%sale_id
				#print sale_order_obj
				#print ''
				#print sale_order_obj[0].date_order
				
				# Para factura es date_invoice
				account_invoice_obj.date_invoice = sale_order_obj[0].date_order
				
				# Se actualiza el campo de la Fecha de la Factura
				print 'Actualizando fecha de factura'
				account_invoice.write(cr, user_id, account_invoice_obj.id, {'date_invoice':account_invoice_obj.date_invoice}, context=context)
				
				# Confirma la Factura
				print 'confirmando la Factura'
				wf_service.trg_validate(user_id, 'account.invoice',invoice_id,'invoice_open', cr)
				
			#9 ENTREGAR PRODUCTOS
			print "============ Entregar Productos ================="
			# Crea objeto stock picking in
			stock_picking_out = self.pool.get('stock.picking.out')
			stock_picking_out_ids = stock_picking_out.search(cr, user_id, [('state','=','confirmed'), ('type','=','out')])
			#~ spo_ids = execute('stock.picking.out', 'search', [('state','=','confirmed'), ('type','=','out')])
			#~ #spo_ids = execute('stock.picking.out', 'search', [('state','=','assigned'), ('type','=','out')])
			#~
			# Recorre los Stock pendientes de enviar
			for stock_picking_out_id in stock_picking_out_ids:
				print "Stock Picking out Id: %s"%(stock_picking_out_id)
				
				pick = stock_picking_out.browse(cr, user_id, stock_picking_out_id)
				
				partial_datas={}
				
				# Recorre los Movimientos de cada picking
				for move in pick.move_lines:
					partial_datas['move%s'%(move.id)]= {
						'prodlot_id':False,
						'product_id': move.product_id.id,
						'product_qty': move.product_qty,
						'product_uom': move.product_uom.id,
						'product_price': move.price_unit,
						#'product_currency': move.price_currency_id,
					}
				partial_datas['delivery_date']= time.strftime('%Y-%m-%d')
				
				# do Partial
				stock_picking_out.do_partial(cr, user_id, [stock_picking_out_id], partial_datas)
				
				# Se limpia partial_datas
				partial_datas.clear()
				
				
				print 'Confirmando en Stock'
				wf_service.trg_validate(user_id, 'stock.picking', stock_picking_out_id,'button_done', cr)
				#print 'Asignando en Stock'
				#wf_service.trg_validate(user_id, 'stock.picking', stock_picking_out_id,'action_move', cr)
				print 'Forzando el Stock'
				wf_service.trg_validate(user_id, 'stock.picking', stock_picking_out_id,'force_assign', cr)
				print 'Procesando el Stock'
				wf_service.trg_validate(user_id, 'stock.picking', stock_picking_out_id,'action_process', cr)
				# este codigo se lo pasaron a Jorge
				#self.pool.get('stock.picking.out').force_assign(cr, user_id, stock_picking_out_id, context)     # confirm  -> assigned  
				#self.pool.get('stock.picking.out').action_move(cr, user_id, stock_picking_out_id, context)      # assigned ->  done
				
				#workflow('stock.picking.out', 'button_done', spo)
				#test_assigned()
				#sm_ids = execute('stock.move', 'search', [('picking_id', '=', spo)])	
				#for sm in sm_ids:
				#print "Id Move # %s"%(sm)
				#workflow('stock.picking.out', 'force_assign', sm)
				
			#workflow('stock.picking.out', 'button_done', spo)
		
		print ""
		print "+FIN DE PROCESO+"
		
	def action_pagarproveedor(self, cr, uid, ids, context = None):
		print '======== Proceso de Pagar Proveedores ==========='
		none = 'Proceso finalizado'
		
		# Crea objeto de Factura
		account_invoice_obj = self.pool.get('account.invoice')
		
		# Crea objeto de Voucher
		account_voucher_obj = self.pool.get('account.voucher')
		
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('login', '=', 'admin_04Merida')])
		print user_ids
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		
		for user_id in user_ids:
			# Se obtiene el usuario con el Id
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Usuario Id:%s'%user_id
			
			invoice_ids = account_invoice_obj.search(cr, user_id, [('state', '=', 'open'), ('type', '=', 'in_invoice'), ('company_id', '=', res_user.company_id.id), ('id', '=', '659')])
			
			# Por cada Factura se crea un voucher
			for invoice_id in invoice_ids:
				invoice = account_invoice_obj.browse(cr, user_id, invoice_id)
				print 'Pagando Factura con Id: %s'%invoice_id
##				print invoice.amount_total
##				print invoice.account_id.id
##				print invoice.date_invoice
##				print invoice.currency_id.id
##				print invoice.partner_id.id
				
				voucher_obj = self.pool.get('account.voucher')
				
				voucher_id = self.pool.get('account.voucher').create(cr, user_id, {
					'name': '',
					'type':'payment',
					'amount':invoice.amount_total,
					'account_id':invoice.account_id.id,
					'date':invoice.date_invoice,
					'payment_option':'without_writeoff',
					'payment_rate_currency_id':invoice.currency_id.id,
					'partner_id':invoice.partner_id.id,
					'reference':invoice.origin,
					'period_id':invoice.period_id.id,
					'pre_line':True,
				}, context=context)
				
				voucher_line_obj = self.pool.get('account.voucher.line')
				
				vline = voucher_line_obj.create(cr, user_id, {
					'voucher_id':voucher_id,
					#'name':invoice.internal_number,
					'name':'',
					'account_id':invoice.account_id.id,
					'amount':invoice.amount_total,
					'amount_original':invoice.amount_total,
					'amount_unreconciled':invoice.amount_total,
					'type': 'dr',
					'date_original':invoice.date_invoice,
					'reconcile':True, 
				}, context=context)
				
##				vline = voucher_line_obj.create(cr, user_id, {
##					'voucher_id':voucher_id,
##					'name':invoice.internal_number,
##					'account_id':invoice.account_id.id,
##					'amount':invoice.amount_total,
##					'amount_original':invoice.amount_total,
##					'amount_unreconciled':invoice.amount_total,
##					'type': 'cr',
##					'date_original':invoice.date_invoice,
##					'reconcile':True, 
##				}, context=context)
				
				voucher_move_line_ids = voucher_obj.voucher_move_line_create(cr, user_id, voucher_id, invoice.amount_total, vline, 34, 34, context)
				
				print voucher_move_line_ids
				
				#print 'Validando el pago con Id: %s'%voucher_id
				#self.pool.get('account.voucher').browse(cr, user_id, voucher_id, context).proforma_voucher(cr, user_id, voucher_id, context)
				#wf_service.trg_validate(user_id, 'account.voucher', voucher_id,'proforma_voucher', cr)
				
				
##			# Se buscan los voucher de tipo pago que estén en borrador
##			voucher_ids = account_voucher_obj.search(cr, user_id, [('state', '=', 'draft'), ('type', '=', 'payment')])
##			print voucher_ids
##			
##			voucher_id = 0
##			for voucher_id in voucher_ids:
##				# Se valida el pago
##				wf_service.trg_validate(user_id, 'account.voucher', voucher_id,'proforma_voucher', cr)
		print '====== Fin de Proceso de Pago a Proveedores ======'
		return none
	
	def ConfirmarCompras(self, cr, uid, ids, context = None):
		# Crea objeto de compra
		purchase_obj = self.pool.get('purchase.order')
		
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('id', '=', uid)])
		#print user_ids
		
		print '=' * 80
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		for user_id in user_ids:
			# Se obtiene
			res_user = res_user_obj.browse(cr, uid, user_id)
			#print 'Usuario Id:%s'%user_id
			
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Se ejecuta el proceso de Compras con el usuario: %s'%res_user.login
			
			# Obtiene las Compras borrador de la empresa del usuario actual
			order_ids = purchase_obj.search(cr, user_id, [('state','=','draft'), ('company_id', '=', res_user.company_id.id)])
			#print 'Compras a confirmar, ids: %s'%order_ids
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(order_ids)
			noRegistroActual = 1
			
			# Crea WorkFlow
			wf_service = netsvc.LocalService("workflow")
			
			#recorre las compras
			order_id = 0
			for order_id in order_ids:
				Mensaje = res_user.login + ' ==> ' + 'Confirmando Compra ' + str(noRegistroActual) + ' de ' + str(totalRegistros)
				print Mensaje
				
				#print 'Confirmando compra:%s'%order_id
				
				# Confirma la Compra
				wf_service.trg_validate(user_id, 'purchase.order',order_id,'purchase_confirm', cr)
			
				# Valida la Compra
				wf_service.trg_validate(user_id, 'purchase.order',order_id,'purchase_approve', cr)
				
				# Se incrementa en uno el número de registro actual
				noRegistroActual = noRegistroActual + 1
	
	def ConfirmarStockCompras(self, cr, uid, ids, context = None):
		# Crea objeto stock picking in
		stock_picking_in_obj = self.pool.get('stock.picking.in')
		
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('id', '=', uid)])
		#print user_ids
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		for user_id in user_ids:
			# Se obtiene el usuario
			res_user = res_user_obj.browse(cr, uid, user_id)
			#print 'Usuario Id:%s'%user_id
			
			print '=' * 80
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Se ejecuta el proceso de Recepción de Inventario con el usuario: %s'%res_user.login
			
			# Crea objeto stock move
			stock_move_obj = self.pool.get('stock.move')
			
			#~ # Busca las Entradas Asignadas de la empresa del usuario actual
			stock_picking_in_ids = stock_picking_in_obj.search(cr,user_id,[('state','=','assigned'), ('type','=','in'), ('company_id', '=', res_user.company_id.id)])
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(stock_picking_in_ids)
			noRegistroActual = 1
			
			# Recorre los Stock pendientes de recibir
			for stock_picking_in_id in stock_picking_in_ids:
				#print 'Stock picking:%s'%stock_picking_in_id
				pick = stock_picking_in_obj.browse(cr, user_id, stock_picking_in_id)
				
				Mensaje = res_user.login + ' ==> Recibiendo Inventario ' + str(noRegistroActual) + ' de ' + str(totalRegistros)
				print Mensaje
				
				partial_datas={}
				
				# Recorre los Movimientos de cada picking
				for move in pick.move_lines:
					partial_datas['move%s'%(move.id)]= {
						'prodlot_id':False,
						'product_id': move.product_id.id,
						'product_qty': move.product_qty,
						'product_uom': move.product_uom.id,
						'product_price': move.price_unit,
						#'product_currency': move.price_currency_id,
					}
				partial_datas['delivery_date']= time.strftime('%Y-%m-%d')
				
				# do Partial
				stock_picking_in_obj.do_partial(cr, user_id, [stock_picking_in_id], partial_datas)
				
				# Se limpia partial_datas
				partial_datas.clear()
				
				noRegistroActual = noRegistroActual + 1
	
	def ConfirmarFacturasCompras(self, cr, uid, ids, context = None):
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('id', '=', uid)])
		print user_ids
		
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		for user_id in user_ids:
			# Se obtiene el usuario
			res_user = res_user_obj.browse(cr, uid, user_id)
			#print 'Usuario Id:%s'%user_id
			
			print '=' * 80
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Se ejecuta el proceso de Confirmación de Facturas de Compras con el usuario: %s'%res_user.login
			
			# Crea objeto de compra
			purchase_obj = self.pool.get('purchase.order')
			
			# Se crea el objeto de Factura
			account_invoice = self.pool.get('account.invoice') # Objeto Principal
			account_invoice_obj = self.pool.get('account.invoice') # Objeto Auxiliar
			
			# Obtiene las Facturas borrador de la empresa del usuario actual
			invoice_ids = account_invoice.search(cr, user_id, [('state','=','draft'), ('type', '=', 'in_invoice'),('company_id', '=', res_user.company_id.id)])
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(invoice_ids)
			noRegistroActual = 1
			
			# Recorre las Facturas
			invoice_id = 0
			for invoice_id in invoice_ids:
				account_invoice_obj = account_invoice.browse(cr, user_id, invoice_id)
				#print 'Factura:%s'%invoice_id
				# Se obtiene la Factura antes de confirmar
				
				Mensaje = res_user.login + ' ==> ' + 'Procesando Factura de Compra ' + str(noRegistroActual) + ' de ' + str(totalRegistros)
				print Mensaje
				
				# Se obtiene la Compra utilizando el Folio de Referencia de la Factura
				order_id = purchase_obj.search(cr, user_id, [('state','=','approved'), ('company_id', '=', res_user.company_id.id), ('name', '=', account_invoice_obj.origin)])
				purchase_order = purchase_obj.browse(cr, user_id, order_id)
				
				# Para factura es date_invoice
				account_invoice_obj.date_invoice = purchase_order[0].date_order
				
				# Se actualiza el campo de la Fecha de la Factura
				account_invoice.write(cr, user_id, account_invoice_obj.id, {'date_invoice':account_invoice_obj.date_invoice, 'supplier_invoice_number':purchase_order[0].name}, context=context)
				
				# Confirma la Factura
				wf_service.trg_validate(user_id, 'account.invoice',invoice_id,'invoice_open', cr)
				
				noRegistroActual = noRegistroActual + 1
	
	def ConfirmarVentas(self, cr, uid, ids, context = None):
		# Crea objeto de Usuario
		res_user_obj = self.pool.get('res.users')
		
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Se buscan todos los Usuarios que sean Administradores
		# user_ids = res_user_obj.search(cr, uid, [('login', 'like', 'admin_%')])
		user_ids = res_user_obj.search(cr, uid, [('id', '=', uid)])
		#print user_ids
		
		# Se recorre cada uno de los Ids de los administradores de cada empresa para ejecutar el proceso
		user_id = 0
		for user_id in user_ids:
			# Se obtiene el usuario administrador
			res_user = res_user_obj.browse(cr, uid, user_id)
			#print 'Usuario Id: %s'%user_id
			
			print '=' * 80
			res_user = res_user_obj.browse(cr, uid, user_id)
			print 'Se ejecuta el proceso de Confirmar Ventas con el usuario: %s'%res_user.login
			
			# Se crea el obtjeto de Ventas
			sale_order = self.pool.get('sale.order')
			# Se obtienen todas las ventas
			sale_ids = sale_order.search(cr, user_id, [('state', '=', 'draft')], limit = 1000) # Se limita la búsqueda a mil registros
			
			#print "============ Confirmar Ventas ================="
			#print 'Ventas: %s'%(sale_ids)
			
			# Se establece el no. total de registros a procesar
			totalRegistros = len(sale_ids)
			noRegistroActual = 1
			
			#4 CONFIRMAR VENTAS
			for sale_id in sale_ids:
				Mensaje = res_user.login + ' ==> Procesando Confirmacion de Venta ' + str(noRegistroActual) + ' de ' + str(totalRegistros)
				print Mensaje
				
				#print "Confirmando Venta Id: %s"%(sale_id)
				#workflow('sale.order', 'order_confirm', so)
				wf_service.trg_validate(user_id, 'sale.order', sale_id,'order_confirm', cr)
				noRegistroActual = noRegistroActual + 1
	
	def ForzarDisponibilidad(self, cr, uid, ids, context = None):
		print "============ Entregar Productos ================="
		
		# Crea WorkFlow
		wf_service = netsvc.LocalService("workflow")
		
		# Crea objeto stock picking out
		stock_picking_out = self.pool.get('stock.picking.out')
		stock_picking_out_ids = stock_picking_out.search(cr, uid, [('state','=','confirmed'), ('type','=','out')], limit = 1000) # Se limita la búsqueda a mil registros
		
		print '=' * 80
		res_user = res_user_obj.browse(cr, uid, uid)
		print 'Se ejecuta el proceso de Forzar Disponibilidad con el usuario: %s'%res_user.login
		
		# Se establece el no. total de registros a procesar
		totalRegistros = len(stock_picking_out_ids)
		noRegistroActual = 1
		
		# Recorre los Stock pendientes de enviar
		for stock_picking_out_id in stock_picking_out_ids:
			Mensaje = res_user.login + ' ==> Forzando Disponibilidad ' + str(noRegistroActual) + ' de ' + str(totalRegistros)
			print Mensaje
			#print "Stock Picking out Id: %s"%(stock_picking_out_id)
			
			pick = stock_picking_out.browse(cr, uid, stock_picking_out_id)
			
			partial_datas={}
			
			# Recorre los Movimientos de cada picking
			for move in pick.move_lines:
				partial_datas['move%s'%(move.id)]= {
					'prodlot_id':False,
					'product_id': move.product_id.id,
					'product_qty': move.product_qty,
					'product_uom': move.product_uom.id,
					'product_price': move.price_unit,
					#'product_currency': move.price_currency_id,
				}
			partial_datas['delivery_date']= time.strftime('%Y-%m-%d')
			
			# do Partial
			stock_picking_out.do_partial(cr, uid, [stock_picking_out_id], partial_datas)
			
			# Se limpia partial_datas
			partial_datas.clear()
			
			print 'Comprobando disponibilidad'
			wf_service.trg_validate(uid, 'stock.picking', stock_picking_out_id,'button_done', cr)
			print 'Forzando disponibilidad'
			wf_service.trg_validate(uid, 'stock.picking', stock_picking_out_id,'force_assign', cr)
			print 'Procesando el Stock'
			wf_service.trg_validate(uid, 'stock.picking', stock_picking_out_id,'action_process', cr)
			
			noRegistroActual = noRegistroActual + 1