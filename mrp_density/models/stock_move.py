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

class stock_move(orm.Model):
	_inherit = 'stock.move'
	
	def write(self, cr, uid, ids, vals, context=None):
		if isinstance(ids, (int, long)):
			ids = [ids]
		data, data_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'group_stock_manager')
		group_id_current_uid = self.pool.get('res.users').search(cr, uid, [('groups_id', '=', data_id)], context=context)
		if uid not in group_id_current_uid:
			frozen_fields = set(['product_qty', 'product_uom', 'product_uos_qty', 'product_uos', 'location_id', 'location_dest_id', 'product_id'])
			for move in self.browse(cr, uid, ids, context=context):
				if move.state == 'done':
					if frozen_fields.intersection(vals):
						raise osv.except_osv(_('Operation Forbidden!'),
											_('Quantities, Units of Measure, Products and Locations cannot be modified on stock moves %s that have already been processed(except by the Stock Manager).') %(move.picking_id.name))
		return  super(stock_move, self).write(cr, uid, ids, vals, context=context)
