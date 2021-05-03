# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 DME Soluciones - http://www.dmesoluciones.com/
#    All Rights Reserved.
#
#	 Coded By: Cindy Yukie Ley (yukieley6@gmail.com)
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

from openerp.osv import osv,fields
from openerp import netsvc
class account_invoice(osv.Model):
	_inherit = 'account.invoice'

	def action_cancel(self, cr, uid, ids, context=None):
		res=super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
		#Si se puede cancelar se va a cambiar el estado de los pos_order de la factura 		
		if res:	
			# Se obtiene el objeto de pos order 
			pos_order= self.pool.get('pos.order')
			wf_service = netsvc.LocalService("workflow")
			# Busco todos los pos order con el id de la factura que se cancelara 
			order_ids= pos_order.search(cr, uid, [('invoice_id', '=', ids[0] )], context=context)
			# Se cambia el estado de facturado a pagado 
			pos_order.write(cr, uid, order_ids, {'invoice_id': None, 'state': 'paid'}, context=context)
			# Se cambia de workflow 
			for pos in order_ids:
				wf_service.trg_validate(uid, 'pos.order', pos, 'paid', cr)
	
		#Regresa el resultado de la cancelacion  		
		return res
