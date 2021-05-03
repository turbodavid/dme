# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com 
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
from openerp.osv import fields, orm

from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp 

class mrp_bom(orm.Model):
	_inherit = 'mrp.bom'
	
	def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
		""" Changes UoM and name if product_id changes.
		@param name: Name of the field
		@param product_id: Changed product_id
		@return:  Dictionary of changed values
		"""
		res = {}
		if product_id:
			res = super(mrp_bom, self).onchange_product_id(cr, uid, ids, product_id, name, context=context)
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			if prod.uos_coeff:
				res['value'].update({
					'product_qty': 1, 
					'product_uos_qty': prod.uos_coeff, 
					'product_uos': prod.uos_id.id,
					'density': prod.density
				})
		return res
		
	def onchange_product_qty(self, cr, uid, ids, product_id, product_qty, context=None):
		res = {}
		if product_id:
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			if prod.uos_coeff:
				res = {'value':{
						'product_uos_qty': product_qty * prod.uos_coeff
					}
				}	
		return res

	def onchange_density(self, cr, uid, ids, product_id, density, product_qty, context=None):
		res = {}
		#view on_change="onchange_density(product_id, density, product_qty)" 
		return res
		
	_columns = {
		'density': fields.float('Density', digits_compute = dp.get_precision('Account'), help=_('Apparent Density (Convertion Factor)')),
	}
