# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 OpenERP s.a. (<http://openerp.com>).
#
#    DME SOLUCIONES
#    Jorge Medina <jorge.medina@dmesoluciones.com>
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
from datetime import datetime, timedelta
import openerp.netsvc
import time
from openerp.tools.translate import _
import operator

class account_move_uuid(orm.Model):
	_name ='account.move.uuid'
	_order = "uuid_view desc"

	def _fn_uuid(self, cr, uid, ids, field, arg, context = None):
		res = {}
		#foreach ids
		for uuid in self.browse(cr, uid, ids, context = context):
			#get type from jounal
			type_journal = uuid.account_move_id.journal_id.type
			#if different to purchase, get uuid
			if type_journal <> 'purchase':
				res[uuid.id] = uuid.uuid
			else:
				#this is a excepction check if have an account in its details, we show its uuids
				excepcion =  "211-03-2-1" # Acreedores Diversos - Nacionales (Diversos)
				#search if uuid is in another policy distinct to actual
				uuid_id = self.search(cr, uid, [('uuid','=',uuid.uuid),('account_move_id','<>', uuid.account_move_id.id)])
				#if not find it, we put it in res{}
				if len(uuid_id)==0:
					res[uuid.id] = uuid.uuid
				else:
					res[uuid.id] = ''
					#searching child account from excepcion
					for line in uuid.account_move_id.line_id:
						#if code is in exepcion, assign uuid
						if excepcion in line.account_id.code:
							res[uuid.id] = uuid.uuid
							break
		#update element to view
		for r in res:
			self.write(cr, uid, [r], {'uuid_view': res[r]}, context)
		return res

	_columns = {
		'guid_ref': fields.char('Guid Ref'),
		'uuid': fields.char('UUID'),
		'account_move_id': fields.many2one('account.move', 'Account Move',  ondelete='cascade'),
		'account_move_line_id': fields.many2one('account.move.line', 'Account Move Line', ondelete='cascade'),
		'uuid_view': fields.char('UUID'),
		'fn_uuid': fields.function(_fn_uuid, type='char',
				string='UUID'
			)
	}
