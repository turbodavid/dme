# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2014 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: Jesus Alfonso Moreno Valdez        alfonso.moreno@pcsystems.mx
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

class stock_picking(orm.Model):
	_inherit = 'stock.picking'

	def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):

		res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)
		factura_id = res.values()
		
		obj_invoice = self.pool['account.invoice'].browse(cr, uid, factura_id[0], context=context)
		#obj_rate = self.pool['stock.picking'].browse(cr, uid, ids[0], context=context)

		update = {'address_issued_id': obj_invoice.journal_id.partner_address_id.id}

		self.pool['account.invoice'].write(cr, uid, factura_id, update)
		return res
