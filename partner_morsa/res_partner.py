# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#    Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
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
from datetime import datetime, timedelta
from openerp.tools.translate import _
class res_partner(osv.Model):
	"""Inherited res_partner"""
	# The line above is the Python’s way to document
	# your objects (like classes)
	_inherit = 'res.partner'

	# Se penso utilizar un field function pero entra en conflicto con año
	def _bithday_date(self, cr, uid, ids, field, arg, context=None):
		result = {}
		for res_partner in self.browse(cr, uid, ids, context=context):
			vat_split = ''
			if res_partner.is_company:
				vat_split = res_partner.vat_split[3:]
			else:
				vat_split = res_partner.vat_split[4:]
			final = vat_split[0:2] + '-' + vat_split[2:4] + '-' + vat_split[4:6] 
			birth_date = datetime.strptime(final, "%Y-%m-%d")
			result[res_partner.id] = birth_date

		return result
	def _days(self, cursor, user_id, context=None):
		return (
			('1',_('Monday')),
			('2',_('Tuesday')),
			('3',_('Wednesday')),
			('4',_('Thursday')),
			('5',_('Friday')),
			('6',_('Saturday')))	
		
	_columns = {        
        'business_name' : fields.char(string="Business Name", size=256),
		'commercial_email' : fields.char(string="Commercial Email", size=256),
		'curp' : fields.char(string="CURP", size=18),
		'course_business' : fields.char(string="Course of Business", size=256),
		'business_manager' : fields.char(string="Business Manager", size=256),
		'purchasing_manager' : fields.char(string="Purchasing Manager", size=256),
		'payment_responsible' : fields.char(string="Responsible for Payments", size=256),
		'photo_business' : fields.binary(string="Photo Business"),
		'photo_IFE' : fields.binary(string="Photo IFE"),
		'photo_authorized_signature' : fields.binary(string="Photo Authorized Signature"),
		#'birthday_date' : fields.function(_bithday_date, type='date', string="Birthday Date"),
		'birthday_date' : fields.date(type='date', string="Birthday Date"),
		'aniversary_date' : fields.date(type='date', string="Aniversary Date"),
		'geophysics_address' : fields.char(string="Geophysics Address", size=256),
		'review_morning_hours' : fields.char(string="review in the morning hours", size=5),
		'review_afternoon_hours' : fields.char(string="review in the afternoon hours", size=5),
		'payment_morning_hours' : fields.char(string="payment in the morning hours", size=5),
		'payment_afternoon_hours' : fields.char(string="payment in the afternoon hours", size=5),
		'review_date' : fields.selection(_days,'Dias'),
		'payment_date' : fields.selection(_days,'Dias'),
		'clasificacion': fields.many2one('clasificacion', ondelete='set null',string="Clasificacion"), 
	}

res_partner()
