# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán	       cesar_sb@hotmail.com
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

class stock_picking_in(orm.Model):
	_inherit = 'stock.picking.in'

	def return_invoice_number(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		for picking in self.browse(cr, uid, ids, context):
			if picking.purchase_id.name:
				purchase_id = picking.purchase_id.id
				origin = "%"+picking.purchase_id.name+"%"
				sql_req= "SELECT supplier_invoice_number FROM account_invoice WHERE origin like '" + origin + "'"
				cr.execute(sql_req)
				num_reg = cr.fetchone()
				if num_reg:
					res[picking.id]  = num_reg[0]
				else:
					res[picking.id]  = None
			else:
				res[picking.id]  = None
		return res

	_columns = {
		'invoice_number' : fields.function(return_invoice_number, method=True, type='char', size=64, string=_('No. de Factura del Proveedor'), store=False),

	}
	
class stock_picking_in(orm.Model):
	_inherit = 'stock.picking'

	def return_invoice_number(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		for picking in self.browse(cr, uid, ids, context):
			if picking.purchase_id.name:
				purchase_id = picking.purchase_id.id
				origin = "%"+picking.purchase_id.name
				sql_req= "SELECT supplier_invoice_number FROM account_invoice WHERE origin like '" + origin + "'"
				cr.execute(sql_req)
				num_reg = cr.fetchone()
				if num_reg:
					res[picking.id]  = num_reg[0]
				else:
					res[picking.id]  = None
			else:
				res[picking.id]  = None
		return res

	_columns = {
		'invoice_number' : fields.function(return_invoice_number, method=True, type='char', size=64, string=_('No. de Factura del Proveedor'), store=False),

	}

