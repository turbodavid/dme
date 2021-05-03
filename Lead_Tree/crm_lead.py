# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#    	Jorge Alfonso Medina Uriarte jorge.medina@dmesoluciones.com
#	 	Cindy Yukie Ley Garcia yukieley6@gmail.com
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
import netsvc
import time
from openerp.tools.translate import _

class crm_lead(osv.Model):
	"""Inherited crm lead"""
	# The line above is the Python’s way to document
	# your objects (like classes)
	_inherit = 'crm.lead'

	def _get_user_create(self, cr, uid, ids, name, args, context=None):
		result = {}
		leads = self.browse(cr, uid, ids, context=context)
		for lead in leads:
			#get the id of the current function of the employee of identifier "i"
			sql_req= """SELECT ru.login FROM crm_lead crm INNER JOIN res_users ru ON (crm.create_uid = ru.id)
		    WHERE (crm.id = %d)""" % (lead.id,)
			cr.execute(sql_req)
			sql_res = cr.dictfetchone()
			if sql_res: #The employee has one associated contract
				result[lead.id] = sql_res['login']
			else:
				result[lead.id] = False
		return result

	def _get_departament(self, cr, uid, ids, name, args, context=None):
		result = {}
		#crea un objeto de tipo res_users para realizar las búsquedas
		users_obj = self.pool.get('res.users')
		#Recorre los leads con los ids enviados
		for lead in self.browse(cr, uid, ids, context=context):
			#obtiene el objeto section, con la section del partner que esta ligado el lead
			user = users_obj.browse(cr,uid, lead.user_id.id, context)
			#agrega al diccionario del lead actual el nombre del user 
			result[lead.id] = user.name
		#regresa resultado
		return result


	def write(self, cr, uid, ids, vals, context=None):		
		for lead in self.browse(cr,uid,ids,context=context):
			if uid == lead.user_id.id or (lead.state == 'draft' and vals.has_key('stage_id') == False):
				return super(crm_lead, self).write(cr, uid, ids, vals, context=context)
			else:
				raise osv.except_osv(_('Error!'), _('Only the manager can change the status of the Initiative'))
				return False

	def _unready(self, cr, uid, ids, name, args, context=None):
		res={}	
		crm_obj= self.pool.get('crm.lead')
		for lead in self.browse(cr,uid,ids,context=context): 	
			if lead.message_unread == True and uid==lead.user_id.id:	
				#se cambia el estado y la etapa('stage_id) a en proceso, el 2 corresponde a esta etapa
				crm_obj.write(cr, uid, [lead.id], {'state': 'open', 'stage_id': 2}, context=context)
		return res



	_columns = {        
		'create_user' : fields.function(_get_user_create, type='char', string="Envió"),
		'departament_name': fields.function(_get_departament, type='char',string='Departament'),
		'unready':fields.function(_unready, type='char',string='Unread'),
	}
