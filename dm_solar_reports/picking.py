# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#       Jorge Alfonso Medina Uriarte <jorge.medina@dmsoluciones.com>
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
from osv import fields,osv
from tools.translate import _

class stock_picking(osv.Model):
	_inherit = 'stock.picking'

	_columns = {
		'filename': fields.char('File Name', size=255, readonly=True),
		'data': fields.binary('File', readonly=True),		
		}

stock_picking()

class stock_picking_out(osv.Model):
	_inherit = "stock.picking.out"

	def generate_csv(self, cr, uid, ids, context=None):	
		# Crea objeto stock move
		stock_move_obj = self.pool.get('stock.move')
		obj_stock = self.pool['stock.picking'].browse(cr, uid, ids[0], context=context)
		if not obj_stock.move_lines:
			raise osv.except_osv(_("Stock Out"), _("You can't generate csv file, because this document don't have move lines."))
		output = ''
		#asign name of file
		filename = "%s.%s" % (obj_stock.name, 'csv')
		#Header
		output = "%s, %s, %s" % (_('Product'), _('Quantity'), _('Serial Number'))
		output += "\n"
		#iterate move lines
		for move in obj_stock.move_lines:
			lot = (move.prodlot_id.name if move.prodlot_id.name else "")
			ref = ("[" + move.prodlot_id.ref + "]" if move.prodlot_id.ref else "")
			line = "%s, %s, %s %s" % (move.name.replace(',',''), move.product_qty, lot, ref)
			output+= line + '\n'
		#encode base64
		out = base64.encodestring(output)
		#save in data base		
		self.write(cr, uid, ids, {'data':out, 'filename':filename}, context=context)
		#return fields 
		result = {'value': {'data': out, 'filename':filename}}
		return result	
	
	_columns = {
		'filename': fields.char('File Name', size=255, readonly=True),
		'data': fields.binary('File', readonly=True),		
           }

stock_picking_out()
