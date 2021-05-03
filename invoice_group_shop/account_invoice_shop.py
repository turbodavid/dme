# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2014 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte (jorge.medina@dmesoluciones.com)
############################################################################
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
from openerp.tools.translate import _

import time

class account_invoice(osv.Model):
	_inherit = 'account.invoice'
	
	def get_shop(self, cr, uid, invoice_id, name, args, context=None):
		res = {}
		# Se recorren cada una de las Facturas
		for invoice in self.browse(cr, uid, invoice_id, context):
			sql_req = """Select ss.name as shop_name
							From account_invoice ai
							Inner Join sale_order so on ai.origin = so.name
							Inner Join sale_shop ss on so.shop_id = ss.id
							Where ai.Id = %d;""" % (invoice.id,)
			cr.execute(sql_req)
			sql_res = cr.fetchall()
			
			# Variable para concatenar las etiquetas encontradas.
			strshop = ''
			
			if sql_res: # Se encontraron registros
				# Se recorren todas las etiquetas encontradas y se concatenan.
				for row in sql_res:
					if(strshop == ''):
						strshop = row[0]
					else:
						strshop += ', ' + row[0]
				
				# Se asigna a la Factura shop
				res[invoice.id] = strshop
			else:
				res[invoice.id] = False

			# Actualiza el campo si es diferente a lo encontrado.
			if(invoice.shop_group != strshop):
				self.write(cr, uid, [invoice.id], {'shop_group': strshop}, context)
			
		return res
		
	_columns = {
		'shop':fields.function(get_shop,
			type='char',
			method=True,
			string='Shop'
			),
		'shop_group' : fields.char('Shop', size=1000, required=True),
	}
	_defaults = {
		'shop':'',
		'shop_group':'Sin Actualizar',
	}
