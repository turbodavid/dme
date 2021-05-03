# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#	 Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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

import os

import openerp
from openerp import SUPERUSER_ID, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import image_resize_image

class res_company(osv.osv):
	_inherit = "res.company"

	def onchange_footer(self, cr, uid, ids, custom_footer, phone, fax, email, website, vat, company_registry, bank_ids, context=None):
		if custom_footer:
			return {}

		# se cambio para no mostrar el VAT jamu
		# first line (notice that missing elements are filtered out before the join)
		res = ' | '.join(filter(bool, [
			phone            and '%s' % (phone),
			fax              and '%s' % (fax),
			email            and '%s' % (email),
			#website          and '%s: %s' % (_('Website'), website),
			#vat              and '%s: %s' % (_('TIN'), vat),
			#company_registry and '%s: %s' % (_('Reg'), company_registry),
			' ',
			
		])) 
		# second line: bank accounts
		res_partner_bank = self.pool.get('res.partner.bank')
		account_data = self.resolve_2many_commands(cr, uid, 'bank_ids', bank_ids, context=context)
		account_names = res_partner_bank._prepare_name_get(cr, uid, account_data, context=context)
		if account_names:
			title = _('Bank Accounts') if len(account_names) > 1 else _('Bank Account')
			res += '\n%s: %s' % (title, ', '.join(name for id, name in account_names))

		return {'value': {'rml_footer': res, 'rml_footer_readonly': res}}
