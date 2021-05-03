# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 DME Soluciones - http://dmesoluciones.com/
#    All Rights Reserved.
#    DME Soluciones
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán            cesar_sb@hotmail.com
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

class purchase_line_invoice(orm.TransientModel):
	_inherit = 'purchase.order.line_invoice'
    
	def makeInvoices(self, cr, uid, ids, context=None):
		res = {}
		if ids:
			if context is None:
				context = {}

			record_ids =  context.get('active_ids',[])
			obj_purchase = self.pool.get('purchase.order.line')
			dat_purchase = obj_purchase.browse (cr, uid, record_ids, context)
			hm = len(dat_purchase)
			index = 0
			partner_list = []
			for partner in dat_purchase:
				partner_list.append(dat_purchase[index].partner_id.id)
				index = index + 1

			index = 0
			chk = False
			if hm > 1:
				while index < hm:
					dato = partner_list[index]
					interno = index + 1
					while  interno < hm:
						if dato <> partner_list[interno]:
							chk = True
							interno = hm
							index = hm
						interno = interno + 1
					index = index + 1
			if chk:
				#res['warning'] = {'title' : "Warning...",'message' : "There are invoices from diferent providers",}
				return self.pool.get('warning').info(cr, uid, title='Make Invoices', message=_("There are invoices from diferent providers"))
			else:
				res = super(purchase_line_invoice, self).makeInvoices(cr, uid, ids, context)
		return res

