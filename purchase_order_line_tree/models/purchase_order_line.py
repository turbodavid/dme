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
from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class purchase_order_line(orm.Model):
	_inherit = 'purchase.order.line'
	
	def _amount_line_new(self, cr, uid, ids, prop, arg, context=None):
		res = {}
		pol_obj = self.pool.get('purchase.order.line')
		pol_id = pol_obj.search(cr, uid, [('price_subtotal_new','=',False)])

		cur_obj = self.pool.get('res.currency')
		tax_obj = self.pool.get('account.tax')
		valor = 0.0
		for line in self.browse(cr, uid, pol_id, context=context):
			taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, line.order_id.partner_id)
			print '***************************************************************************************'
			print 'linea', line.id
			cur = line.order_id.pricelist_id.currency_id
			valor = cur_obj.round(cr, uid, cur, taxes['total'])
			#pol_obj.write(cr, uid, line.id, {'price_subtotal_new':res[line.id]}, context)
			cr.execute('update purchase_order_line pol set price_subtotal_new = ' + str(valor) + ' where id = %d;' % (line.id))
		return res
	
	_columns = {
		'price_subtotal_1': fields.function(_amount_line_new, string='Subtotal', digits_compute= dp.get_precision('Account')),
        	'price_subtotal_new': fields.float('Subtotal', digits_compute= dp.get_precision('Account')),
	}

