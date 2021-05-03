# -*- encoding: utf-8 -*-
# -*- coding: 850 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán (cesar_sb@hotmail.com)
############################################################################
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
import base64
import csv
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import datetime, time
import openerp.addons.decimal_precision as dp 
from openerp import tools
import os

class complete_sales(orm.TransientModel):
	_name = 'complete.sales'
	_description = 'Complete Sales Form'

	_defaults = {
		'report_type' : 'invoice',
		#'company_id'  : '1',
		'date_rep'    : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
		'date_ini'    : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
		'date_fin'    : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
	}


	_columns = {
		'report_type' : fields.selection([('invoice', 'Invoice'), ('product', 'Product')], 'Report Type', required=True),
		'company_id'  : fields.many2one('res.company', 'Company', required=True),
		'date_rep'    : fields.date('Close date', required=True),
		'date_ini'    : fields.date('Initial date', required=True),
		'date_fin'    : fields.date('Finish date', required=True),
		'filename'    : fields.char('File Name', size=255, readonly=True),
		'data'        : fields.binary('File', readonly=True),
	}

	def default_get(self, cr, uid, fields, context=None):
		res = super(complete_sales, self).default_get(cr, uid, fields, context=context)
		res['company_id'] = 1
		return res

	def eSg(x, cadena):
		nueva_cadena = ''
		if cadena > '':
			for l in cadena:
				x = l		
				if x == u'Ñ':
					x = 'N'
				elif x == u'ñ':
					x = 'ñ'
				elif x == u'Á':
					x = 'A'
				elif x == u'É':
					x = 'E'
				elif x == u'Í':
					x = 'I'
				elif x == u'Ó':
					x = 'O'
				elif x == u'Ú':
					x = 'U'
				elif x == u'Ü':
					x = 'U'
				elif x == u'á':
					x = 'a'
				elif x == u'é':
					x = 'e'
				elif x == u'í':
					x = 'i'
				elif x == u'ó':
					x = 'o'
				elif x == u'ú':
					x = 'u'
				nueva_cadena = nueva_cadena + x
		if nueva_cadena == '':
			nueva_cadena = str(cadena)
		return nueva_cadena

	def execute_query(self, cr, uid, ids, context=None):
		# Crea objeto complete sales
		obj_sales = self.pool['complete.sales'].browse(cr, uid, ids[0], context=context)
		if not obj_sales:
			raise osv.except_osv(_("Sales"), _("You can't generate csv file, because this document don't have sales."))

		report   = obj_sales.report_type
		comp_id  = obj_sales.company_id.id
		date_ini = obj_sales.date_ini
		date_fin = obj_sales.date_fin
		date_cls = obj_sales.date_rep
		#-- Encabezado de Ventas Integrales por Factura
		strquery_1 = ( "SELECT * FROM ( "
					   		"SELECT DISTINCT rp2.name as Vendedor, ccs.name Zona, ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, "
											"ai.number Factura, ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, "
											"ai.amount_tax / CASE ai.amount_untaxed WHEN 0 THEN 1 ELSE ai.amount_untaxed END TasaImpuestos, ai.amount_untaxed Subtotal, "
					   						"ai.amount_tax Impuestos, ai.amount_total Total, ai.residual  SaldoActual, payment.last_rec_date DiaPago, "
					   						"ai.amount_total - fn_get_payment_acum(ai.move_id, payment.date_payment) SaldoCorte, get_categ_firstlevel(pt.categ_id) Familia "
					   		"FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
					   							"INNER JOIN product_template pt ON (ail.product_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
					   							"INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
					   							"LEFT JOIN crm_case_section ccs ON (ai.section_id = ccs.id) INNER JOIN account_journal aj ON (ai.journal_id = aj.id)"
					   							"LEFT JOIN fn_get_payment(ai.move_id, '" + date_cls + "') Payment ON (ai.move_id = payment.move_id) "
							"WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_invoice') AND ai.state IN ('open','paid') "
							"UNION "
							"SELECT DISTINCT rp2.name as Vendedor, ccs.name Zona, ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, "
											"ai.number Factura, ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, "
											"-ai.amount_tax / CASE ai.amount_untaxed WHEN 0 THEN 1 ELSE ai.amount_untaxed END TasaImpuestos, -ai.amount_untaxed Subtotal, "
											"-ai.amount_tax Impuestos, -ai.amount_total Total, -ai.residual SaldoActual, payment.last_rec_date DiaPago, "
											"-(ai.amount_total - fn_get_payment_acum(ai.move_id, payment.date_payment)) SaldoCorte, get_categ_firstlevel(pt.categ_id) Familia "
							"FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
												"INNER JOIN product_template pt ON (ail.product_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
												"INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
												"LEFT JOIN crm_case_section ccs ON (ai.section_id = ccs.id) INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
												"LEFT JOIN fn_get_payment(ai.move_id, '" + date_cls + "') Payment ON (ai.move_id = payment.move_id) "
							"WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_refund') AND ai.state IN ('open','paid')) tbl "
						"ORDER BY  Cliente, FechaFactura, DiaPago" )

		#--va el detallado de Ventas Integrales por Producto
		strquery_2 = ( "SELECT * FROM ("
					   		"SELECT rp2.name as Vendedor, ccs.name Zona,  ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, ai.number Factura, "
									"ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, get_categ_firstlevel(pt.categ_id) Familia, "
									"pt.name NombreProducto, get_categ_secondlevel(pt.categ_id,1) Linea, pc.name Proveedor, ail.quantity Cantidad, "
					   				"ail.price_subtotal Venta, 0 Devolucion, 0 Bonificacion "
					   		"FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
					   								"INNER JOIN product_template pt ON (ail.product_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
					   								"INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
					   								"LEFT  JOIN crm_case_section ccs ON (ai.section_id = ccs.id) "
					   								"INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
					   								"LEFT JOIN fn_get_payment(ai.move_id, '" + date_cls + "') Payment ON (ai.move_id = payment.move_id) "
							"WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_invoice')  AND ai.state IN ('open','paid') "
							"UNION "
							"SELECT rp2.name as Vendedor, ccs.name Zona, ai.move_id, ai.partner_id, rp.name Cliente, rp.vat_split RFC, aj.name Sucursal, ai.number Factura, "
									"ai.type TipoDocto, ai.state Estatus, ai.date_invoice FechaFactura, ai.date_due Vencimiento, get_categ_firstlevel(pt.categ_id) Familia, "
									"pt.name NombreProducto, get_categ_secondlevel(pt.categ_id,1) Linea, pc.name Proveedor, CASE WHEN ai.origin IS NULL THEN 0 ELSE -ail.quantity END Cantidad, "
									"0 Venta, CASE WHEN ai.origin IS NOT NULL THEN -ail.price_subtotal ELSE 0 END Devolucion, CASE WHEN ai.origin IS NULL THEN -ail.price_subtotal ELSE 0 END Bonificacion "
							"FROM account_invoice ai INNER JOIN res_partner rp ON (ai.partner_id = rp.id) INNER JOIN account_invoice_line ail ON (ail.invoice_id = ai.id) "
													"INNER JOIN product_template pt ON (ail.product_id = pt.id) INNER JOIN product_category pc ON (pt.categ_id = pc.id) "
													"INNER JOIN res_users ru ON (ai.user_id = ru.id) INNER JOIN res_partner rp2 ON (ru.partner_id = rp2.id) "
													"LEFT JOIN crm_case_section ccs ON (ai.section_id = ccs.id) INNER JOIN account_journal aj ON (ai.journal_id = aj.id) "
													"LEFT JOIN fn_get_payment(ai.move_id, '" + date_cls + "') Payment ON (ai.move_id = payment.move_id) "
							"WHERE ai.date_invoice BETWEEN '" + date_ini + "' AND '" + date_fin + "' AND ai.type IN ('out_refund') AND ai.state IN ('open','paid')) tbl "
						"ORDER BY  Cliente, FechaFactura" )

		strquery = ''
		output = ''
		result = {}
		encabezado = ''
		if report == 'invoice':
			strquery = strquery_1
			encabezado = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ( _('vendedor'), _('zona'),_('move_id'),_('partner_id'),_('cliente'),_('rfc,sucursal'),_('factura'),_('tipodocto'),_('estatus'),_('fechafactura'),_('vencimiento'),_('tasaimpuestos'),_('subtotal'),_('impuestos'),_('total'),_('saldoactual'),_('diapago'),_('saldocorte'),_('familia'))
		else:
			strquery = strquery_2
			encabezado = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (_('vendedor'),_('zona'),_('move_id'),_('partner_id'),_('cliente'),_('rfc'),_('sucursal'),_('factura'),_('tipodocto'),_('estatus'),_('fechafactura'),_('vencimiento'),_('familia'),_('nombreproducto'),_('linea'),_('proveedor'),_('cantidad'),_('venta'),_('devolucion'),_('bonificacion'))

		cr.execute(strquery)
		registros = cr.fetchall()

		filename = ''
		if registros:
			#asign name of file
			#filepath = "%s" % ('/home/jorge-medina/pyerp7/parts/extras/dme/complete_sales/data/')
			filepath = '%s/%s/' % (os.path.dirname(os.path.abspath('')),'local_modules/complete_sales/data')
			filename = "%s.%s" % ('reporte_' + report + '_' + date_cls, 'csv')
			filefull = "%s" % (filepath + filename)
			#Header
			output = encabezado 
			output += "\n"
			#Abre archivo de salida CSV
 			csvsalida = open(filefull, 'w')
			#iterate move lines
			for move in registros:
				# Genera la linea de salida
				#line = "%s, %s, ..." % (move[0].decode('UTF-8'), move[1].decode('UTF-8'), ...)
				line = ''
				x=0
				while x<20:
					dato = self.eSg(move[x])
					if move[x] != '':
						dato = '"' + dato + '"'
						line += dato
					else:
						line += ','
					if x<=18:
						line += ','
					x = x + 1
				line = self.eSg(line)
				csvsalida.write(line + '\n')
				output += line + '\n'
			csvsalida.close()
			#encode base64
			out = base64.encodestring(output)
			#save in data base
			self.write(cr, uid, ids, {'data':out, 'filename':filename}, context=context)
			dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'complete_sales', 'complete_sales_view_data')
			return {'name': _("Complete Sales"),
                'res_model':"complete.sales",
                'src_model':"complete.sales",
                'view_mode':"form",
                'target':"new",
                'key2':"client_action_multi",
                'multi':"True",
                'res_id':ids[0],
                'view_id':view_id,
                'type': 'ir.actions.act_window',
			}
		else:
			return self.pool.get('warning').info(cr, uid, title='Reports', message=("there is no information with parameters provided."))

complete_sales()
