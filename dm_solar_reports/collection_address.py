# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
#
#	 Coded By:
#	 	Cindy Yukie Ley Garcia (cindy.ley@dmesoluciones.com) 
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

class colletion_address(osv.Model):
	_name= "collection.address"
	_rec_name = 'place_site'
	
	def join_address(self, cr, uid, id, name, args, context=None):
		result = {}
		obj_coll= self.pool.get('collection.address')
		for obj_data in obj_coll.browse(cr, uid,id, context=context):
			result[obj_data.id] = "%s %s %s %s %s %s %s %s" % (obj_data.colony_site or '', obj_data.state_id_site.name or '', obj_data.number_site or '', obj_data.state_id_site.name or '', obj_data.street_site or '', obj_data.city_id_site.name or '', obj_data.zip_site or '', obj_data.phone_site or '')

		return result 

	def on_change_city(self, cr, uid, ids, city_id, context=None):
		result = {}
		if context is None:
			context = {}
		if city_id:
			obj_city = self.pool['res.country.state.city'].browse(cr, uid, city_id, context=context)
			result = {'value': {'state_id_site': obj_city.state_id.id if obj_city.state_id else False}
					}
		return result
			
	_columns = {
		'place_site': fields.char('Place', size=255, required = True ),
		'street_site': fields.char('Street', size=128),
		'colony_site': fields.char('Colony', size=128),
		'city_id_site': fields.many2one('res.country.state.city', 'City'),
		'number_site': fields.char('Number', size=128),
		'zip_site': fields.char('Zip', size=24),
		'state_id_site': fields.many2one('res.country.state', 'State'),
		'phone_site': fields.char('Phone', size=64),
		'campo_function':fields.function(join_address, type= "String", string= "Address"),
		'contact_site': fields.char('Contact', size=128)
	}

