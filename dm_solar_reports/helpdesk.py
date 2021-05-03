# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#	 	Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
#		Cindy Yukie Ley Garcia cindy.ley@dmesoluciones.com
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
class crm_helpdesk(osv.Model):
	_inherit=  'crm.helpdesk'

	def create(self, cr, uid, vals, context=None):
		if vals.get('folio','/')=='/':
			vals['folio'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.helpdesk') or '/'
		return super(crm_helpdesk, self).create(cr, uid, vals, context=context)

	_columns= {
		'folio' :  fields.char('Helpdesk Reference', size=64, required=True,
			readonly=True, select=True), 
	}

	_defaults = {
		'folio': lambda self, cr, uid, context: '/',
	}

