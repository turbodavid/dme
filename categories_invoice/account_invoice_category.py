# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2014 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jesus Meza(jesus.meza@dmesoluciones.com)
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
	
	def ObtenerEtiquetas(self, cr, uid, invoice_id, name, args, context=None):
		res = {}
		# Se recorren cada una de las Facturas
		for invoice in self.browse(cr, uid, invoice_id, context):
			sql_req = """Select C.name
						From res_partner_res_partner_category_rel R
							Inner Join res_partner_category C On R.category_id = C.id
						Where (R.partner_id = %d)
						Order By C.id""" % (invoice.partner_id.id,)
			cr.execute(sql_req)
			sql_res = cr.fetchall()
			
			# Variable para concatenar las etiquetas encontradas.
			stretiqueta = ''
			
			if sql_res: # Se encontraron registros
				# Se recorren todas las etiquetas encontradas y se concatenan.
				for row in sql_res:
					if(stretiqueta == ''):
						stretiqueta = row[0]
					else:
						stretiqueta += ', ' + row[0]
				
				# Se asigna a la Factura las etiquetas encontradas
				res[invoice.id] = stretiqueta
			else:
				res[invoice.id] = False
			
			# Actualiza el campo si es diferente a lo encontrado.
			if(invoice.categories_group != stretiqueta):
				self.write(cr, uid, [invoice.id], {'categories_group': stretiqueta}, context)
			
		#print res
		return res
		
	_columns = {
		'categories':fields.function(ObtenerEtiquetas,
			type='char',
			method=True,
			string='Category'
			),
		'categories_group' : fields.char('Categories', size=500, required=False),
	}
	_defaults = {
		'categories':'',
		'categories_group':'',
	}