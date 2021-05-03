# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 OpenERP s.a. (<http://openerp.com>).
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

class account_move_line(orm.Model):
	_inherit ='account.move.line'
    
	def browse_uuid(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		#object data
	        models_data = self.pool.get('ir.model.data')
	        #search view
	        view_id = models_data.search(cr, uid,  [('module', '=', 'sync_gmm'), ('name','=','wizard_account_move_line_uuid')])
	        #browse record
	        view_id = models_data.browse(cr, uid,  view_id)
	        #get id
	        view_id = view_id[0].res_id
		#show view
		return {
			'name' : _('Account Move Line UUID'),
			'type': 'ir.actions.act_window',
			'res_model': 'account.move.line',
			'view_mode': 'form',
			'view_type': 'form',
			'view_id': view_id, 
			'target': 'new',
			'context':  context,
			'res_id': ids[0]
        	}

	def save_uuid_line(self, cr, uid, ids, context=None):
		return {}

	_columns = {
		'account_move_line_ids': fields.one2many('account.move.uuid', 'account_move_line_id' ,'Account Move Line UUID'),
		'uuid' : fields.char('UUID'),
		'guid': fields.char('GUID'),
	}
  
