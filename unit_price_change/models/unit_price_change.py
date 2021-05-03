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
import openerp.addons.decimal_precision
 
class purchase_order_line(orm.Model):
	_inherit = 'purchase.order.line'
    
	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id, date_planned, name, price_unit, context=None):
		res={}
		if product_id:
			current_id = 0
			if context is None:
				context = {}

			lista = [] 
			lista.append(product_id)
			obj_template = self.pool.get('product.template')
			dat_template = obj_template.browse (cr, uid, lista, context)
			price_unit = dat_template[0].standard_price

			sql_req= """SELECT order_id, price_unit, pricelist_id, ppl.currency_id FROM purchase_order_line pol
					INNER JOIN purchase_order po ON (pol.order_id = po.id)
					INNER JOIN product_pricelist ppl ON (po.pricelist_id = ppl.id)
					WHERE pol.partner_id = %d and product_id = %d ORDER BY pol.id DESC LIMIT 1;""" % (partner_id, product_id)
			cr.execute(sql_req)
			products = cr.fetchall()
			num_prod = len(products)
			if num_prod > 0:
				price_unit = products[0][1]
				current_id = products[0][3]

				ppl_reg = self.pool.get('product.pricelist').browse (cr, uid, pricelist_id, context)			
				cur_obj = self.pool.get('res.currency')
                    		price_unit = cur_obj.compute(cr, uid, current_id, ppl_reg.currency_id.id, price_unit)
			
			res = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id, 				    partner_id, date_order, fiscal_position_id, date_planned, name, price_unit, context=context)
			if res.has_key('warning'):
				cr.execute("select type from product_template where id = " + str(product_id))
				prod = cr.fetchone()[0]
				if prod != 'service':
					res['warning'] = {'title' : "Warning...",'message' : _("This Product doesn't belong to this Supplier."),}
			else:
				res['value']['price_unit'] = price_unit  # Actualiza el ultimo precio
		return res

		product_id_change = onchange_product_id

