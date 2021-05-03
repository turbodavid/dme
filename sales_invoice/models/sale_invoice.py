# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2014 DME Soluciones - http://www.dmesoluciones.com
#    All Rights Reserved.
############################################################################
#    Coded by: César Alfredo Sánchez Beltrán        cesar_sb@hotmail.com
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
	_inherit = 'account.invoice'

	def onchange_user_id(self, cr, uid, ids, user_id, context=None):
		val = {'section_id': False}
		if not user_id:
			return {'value': val}

		reg_crm = None
		statement = "select ccs.id, ccs.name from res_users ru inner join crm_case_section ccs on (ccs.id = ru.default_section_id) 				     where ru.id = " + str(user_id)
		cr.execute (statement)
		reg_crm = cr.fetchone()
		if reg_crm:
			val = {'section_id' : reg_crm[0]}
		
	        return {'value': val}
	

	def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id, context=None):
		if not partner_id:
			val = {'user_id': False}
		else:
			statement = "select user_id from res_partner where id = " + str(partner_id)
			cr.execute (statement)
			reg_part = cr.fetchone()
			if reg_part:
				user_id = reg_part[0]
			else:
				user_id = False
		
		res = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id, context=None)
		res['value']['user_id'] = user_id
		return res

