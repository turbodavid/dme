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
from openerp.osv import orm,fields
from openerp.tools.translate import _

WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]

class warning(orm.TransientModel):
	_name = 'warning'
	_description = 'warning'
	_columns = {
		'type': fields.selection(WARNING_TYPES, string='Type', readonly=True),
		'title': fields.char(string="Title", size=100, readonly=True),
		'message': fields.text(string="Message", readonly=True),
		}
	_req_name = 'title'

	def _get_view_id(self, cr, uid):
		"""Get the view id
		@return: view id, or False if no view found
		"""
		# ----------------------------------------------------------------- module name       view name
		res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'message_box', 'warning_form')
		return res and res[1] or False

	def message(self, cr, uid, id, context):
		message = self.browse(cr, uid, id)
		message_type = [t[1]for t in WARNING_TYPES if message.type == t[0]][0]
		view_id = self._get_view_id(cr, uid)
		res = {
			'name': '%s: %s' % (_(message_type), _(message.title)),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'res_model': 'warning',
			'domain': [],
			'context': context,
			'type': 'ir.actions.act_window',
			'target': 'new',
			'res_id': message.id
			}
		return res

	def warning(self, cr, uid, title, message, context=None):
		id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'warning'})
		res = self.message(cr, uid, id, context)
		return res

	def info(self, cr, uid, title, message, context=None):
		id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'info'})
		res = self.message(cr, uid, id, context)
		return res

	def error(self, cr, uid, title, message, context=None):
		id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'error'})
		res = self.message(cr, uid, id, context)
		return res
