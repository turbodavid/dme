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
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc

class mrp_production(orm.Model):
	_inherit = 'mrp.production'

	def _get_standard_price(self, cr, uid, ids, fields, arg, context):
		res={}
		account_move_line_obj = self.pool.get('account.move.line')
		for record in self.browse(cr, uid, ids):
	            #we search in policy 
	            lines =  account_move_line_obj.search(cr, uid, [('name', '=', record.name), ('product_id', '=', record.product_id.id), ('credit', '>',0)])
	            if len(lines)>0:
	                for l in lines:
	                    obj_line = account_move_line_obj.browse(cr, uid, l, context=context)
	                    if record.product_qty > 0:
	                        res[record.id]= obj_line.credit/record.product_qty
	                    else:
	                        res[record.id]= 0.0
	            else:
	                res[record.id]= 0.0
		return res
        
	_columns = {
		'standard_price': fields.function(_get_standard_price, method=True, type='float', string='Standard Price (Unit)', digits_compute=dp.get_precision('Account')),
	}
