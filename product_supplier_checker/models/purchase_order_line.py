# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán           cesar_sb@hotmail.com 
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
from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class purchase_order_line(orm.Model):
	_inherit = 'purchase.order.line'
    
	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id, date_planned, name, price_unit, context=None):
		res = {}
		if product_id:
			"""
			onchange handler of product_id
			"""
			if context is None:
				context = {}

			cr.execute("select type from product_template where id = " + str(product_id))
			prod = cr.fetchone()[0]
			if prod != 'service':
				sql_req= """select name from product_supplierinfo psi where psi.name = %d and psi.product_id = %d;""" 						% (partner_id, product_id)
				cr.execute(sql_req)
				supplier = cr.fetchall()
				num_sup = len(supplier)    # Toma el numero de Proveedores
				if num_sup == 0:
					res['warning'] = {'title' : "Warning...",'message' : _("This Product doesn't belong to this Supplier..."),}
					return res
			
			res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id, date_planned, name, price_unit, context)
		
		return res

		product_id_change = onchange_product_id

