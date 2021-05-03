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



"""Inherit res.currency to handle accounting date values when converting currencies"""
class res_currency_account(orm.Model):
	_inherit = "res.currency"

	def _get_conversion_rate(self, cr, uid, from_currency, to_currency, context=None):
		context = context.copy()
		if context is None:
			context = {}

		if context.get('force_currency_rate',False):
			del context['force_currency_rate']

		rate = super(res_currency_account, self)._get_conversion_rate(cr, uid, from_currency, to_currency,
																	  context=context)
		return rate

res_currency_account()
