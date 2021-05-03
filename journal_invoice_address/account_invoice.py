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

class account_invoice(orm.Model):
	_inherit = 'account.invoice'

	def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
		
		obj_journal = self.pool['account.journal'].browse(cr, uid, journal_id, context=context)
		
		res = super(account_invoice, self).onchange_journal_id(cr, uid, ids, journal_id, context)
		res ['value']['address_issued_id'] = obj_journal.partner_address_id.id
		return res